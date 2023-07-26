from types import SimpleNamespace
from typing import Optional

import tatsu
from tatsu.exceptions import FailedParse

from agtool.abstract import AbstractController
from agtool.error import InvalidModelData
from agtool.interfaces.reader import AGReader
from agtool.struct.graph import Graph
from agtool.struct.vertex import Vertex, VertexEdge


class AGTxtReader(AGReader):
    """
    A reader for the txt file format for agtool. This is a simple,
    human-readable file format intended to allow end users to quickly generate
    an account graph based on a known specification - or to experiment with
    specifications.
    """

    # The grammar definition for the AGTool txt language.
    __GRAMMAR = '''
    @@grammar::AGTOOL_TXT
    
    @@parseinfo :: True
    
    # End-of-line comments may be specified with #, % or //.
    @@eol_comments :: /[#|%|\/\/].*?$/
    
    # First rule - parsing starts here. NOTE THAT ORDER MATTERS - placing rules
    # before this one will cause them to be come the new start rule.
    start = line $ ;
    
    # Include-able rule that swallows a whitespace character.
    SWALLOW_WHITESPACE = /(\s)*/ ;
    
    # Include-able rule that swallows an end-of-line - here just denoted by
    # CR, CRLF or LF.
    # Additionally, a semicolon line delimiter has been included for
    # convenience or personal preference.
    # Finally, zero or more space characters are permitted before and after an
    # EOL.
    eol = /(\s)*(\r|\r\n|\n|;)(\s)*/ ;
    
    # A line is 0 or more newline-seperated expressions.
    line = $ | @+:expression { >eol [ @+:expression ] } ;
    
    # Denotes a possible expression that may occur on a line.
    # Each expression type is labelled with 'expression_type' and a constant
    # name, with the data available under the 'expression' key for easy
    # processing.
    expression
        =
        | expression_type:`set_edges`       expression:set_edges
        | expression_type:`set_attributes`  expression:set_attributes
        | expression_type:`set_types`       expression:set_types
        | expression_type:`macro`           expression:macro
        ;
    
    # The syntax used to set key-value attributes on each vertex is one of:
    #
    # key=value: vertexes
    # vertexes: key=value
    #
    # For example:
    # os=android: phone1, phone2
    # phone1, phone2: os=android
    # 
    # Or, alternatively a shorthand for setting the 'description' key on all
    # vertices is as follows:
    #
    # * vertexList: description
    #
    # For example:
    # * phone1, phone2: Phones belonging to John Smith
    set_attributes =
        | key:key '=' value:VALUE ':' vertexList:vertex_list
        | vertexList:vertex_list ':' key:key '=' value:VALUE
        | key:`description` '*' vertexList:vertex_list ':' value:VALUE
        ;
    
    # The syntax used to set types is the type key on the LHS of a colon,
    # followed by the list of vertexes with that type.
    # 
    # For example:
    # device: phone1, phone2 
    set_types = type:key ':' vertexList:vertex_list ;
    
    # The syntax used to link vertices together is a list of vertices, followed
    # by an arrow, and then followed by another list of vertices. Optionally,
    # with a description that will be added to all of the vertices on the RHS
    # of the arrow (i.e., vertexList2).
    #
    # When a vertex list is specified on the LHS of an arrow, it is considered
    # to be a dependency for all of the vertices on the RHS of the arrow.
    # That is, ALL of the vertices on the LHS are required to access ANY of the
    # vertices on the RHS. (It should be sufficient to handle these semantics by
    # generating a group ID for the LHS vertices and storing this in the
    # edges to the RHS vertices).
    #
    # Note, as a point of clarification, when the LHS is a list and the RHS is
    # a list, the LHS is considered to be a dependency for each of the RHS
    # vertices. So for each RHS vertex, there will be an edge from each LHS
    # vertex to it and all of these edges from the LHS to a given RHS vertex
    # will be grouped together.
    #
    # For example:
    #
    # password -> Gmail
    set_edges = vertexList1:vertex_list link:ARROW ~ vertexList2:vertex_list [ >SWALLOW_WHITESPACE ':' >SWALLOW_WHITESPACE description:VALUE ] ;
    
    # Macros allow a given symbol to be substituted for an edge label.
    # New macros can be defined in the file with the following syntax:
    # @symbol:name
    #
    # For example:
    # @~:fun
    #
    # This would create a macro such that edges denoted with ~> are labelled as
    # 'fun', ~~> are labelled as 'funfun', etc.,
    # Presently macro symbols cannot be - or =. This is defined both at the
    # regex level and in the implementation when processing the AST as a design
    # choice for greater clarity in files.
    macro = '@' symbol:SYMBOL ':' substitution:edge_label ;
    
    # A collection of one or more vertices.
    vertex_list = @+:key { ',' @+:key } ;
    
    ##########################################################################
    
    # A compact way of representing the arrow types which must start with
    # either - or = and may optionally contain an edge label.
    # = is intended as a syntactic sugar for 'rec' (recovery method) and will
    # cause the label of the arrow to be overwritten with 'rec'.
    # - is permitted within the label, and is replaced with the empty string.
    ARROW = linkType:('-'|'='|SYMBOL) label:[edge_label] '>';
    
    # An edge label such as 'rec' may be supplied to an ARROW to indicate the
    # type of edge.
    edge_label = /[a-zA-Z-=]+[a-zA-Z0-9\-=]*/ ;
    
    # key is a generic regular expression for the name of a vertex.
    key = /[a-zA-Z]+[a-zA-Z0-9_]*/ ;
    
    # SYMBOL is a possible symbol for a macro. It MUST NOT be either
    # alphanumeric or be one of the existing arrow symbols (and nor an arrow
    # head, >).
    SYMBOL = /[^>a-zA-Z0-9\-=]{1}/ ;
    
    # VALUE is a possible symbol for a description or some other value.
    # This will match one or more characters, excluding a colon or newline. If
    # this needs to be more constrained, the below suggestion could be used or
    # modified.
    VALUE = /[^:\r\n]+/ ;
    '''

    # The default set of macros for arrows.
    __DEFAULT_MACROS = {'=': 'rec'}

    @property
    def name(self) -> str:
        return "agtool Format Reader (txt)"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def author(self) -> str:
        return "SamJakob"

    @property
    def license(self) -> str:
        return "MIT"

    @property
    def default_file_extension(self) -> str:
        return "txt"

    def __init__(self, controller):
        super().__init__(controller)

        # Compile the model and Abstract Syntax Tree.
        self.controller.logger.debug("Compiling text file grammar model...")
        self.model = tatsu.compile(AGTxtReader.__GRAMMAR)
        self.controller.logger.debug("Finished text file compiling grammar model...")

    def read_graph(self, input_source_name: str, input_data: str) -> Optional[Graph]:
        ast: Optional

        self.controller.logger.info(f"Parsing {input_source_name} as agtool format...")

        try:
            ast = self.model.parse(input_data)
        except FailedParse as ex:
            self.controller.logger.debug("Parser error:\n" + str(ex))

            line_info = ex.tokenizer.line_info(ex.pos)

            raise InvalidModelData(
                description=f'Error on line {line_info.line + 1} (pos. {line_info.col + 1}).\n'
                            f'{ex.item}, got: "{line_info.text.rstrip()}".',
                controller=self.controller,
                input_source=input_source_name,
            ).with_traceback(None) from None

        if ast is None:
            self.controller.logger.warning(f"{input_source_name} is empty... Producing empty graph.")
            return None

        # Store the parsed information.
        macros: dict[str, str] = AGTxtReader.__DEFAULT_MACROS
        """
        Stores macro substitutions - the key is the symbol for the macro, and
        the value is the substitution.
        """

        vertex_types: dict[str, str] = {}
        """
        Stores vertex type definitions. When set_types is invoked on a line,
        the type for the vertex is stored here, this is then passed to the
        vertex object when it is created.
        
        The key is the unique vertex name, and the value is the type.
        
        If a vertex has not been initialized in vertex_types, it will throw an
        error if it is subsequently referenced.
        
        Future re-definitions of vertex type are indicative of an error and
        will therefore throw an error.
        """

        vertex_attributes: dict[str, dict[str, any]] = {}
        """
        Stores attributes for vertices. When set_attributes is invoked,
        the attributes are stored here, then this is passed into the vertex
        object when it is created.
        
        The key is the name of the vertex and the value is the dictionary
        containing the attributes to be assigned to the vertex.
        
        If a vertex has not been initialized in vertex_types, it will throw an
        error if it is subsequently referenced.
        """

        vertex_edges: dict[str, list[VertexEdge]] = {}
        """
        Stores the edges for vertices. When set_edges is invoked on a line,
        each LHS vertex (vertexList1) is stored (or updated) as a key here,
        where the value is a list of vertexes that are adjacent to the key.
        
        Once these edges are applied to a Vertex, the VertexEdge object created
        here will be transferred to the Vertex object.
        
        If a vertex has not been initialized in vertex_types, it will throw an
        error if it is subsequently referenced.
        """

        group_counter: dict[str, int] = {}
        """
        Stores the current group counter for each vertex. This is used to
        generate a unique group ID for each set of vertices on the LHS of an
        arrow (where the ID is unique per RHS vertex).
        
        The key of this dictionary is the name of the RHS vertex, and the value
        is the current group ID for that vertex.
        """

        unique_group_counter: int = 0
        """
        Stores the current unique group counter. This is used to generate a
        unique group ID for each conjunction of vertices similarly to group_counter
        but for the entire graph, rather than being unique to the RHS vertex.
        """

        def assign_vertex_attribute(assign_to: str, key: str, value: any):
            # This function assumes that the assign_to vertex has already been
            # defined as a vertex in attributes!

            # Check if there is a set of attributes for that vertex
            # already. If not, initialize an empty dictionary to
            # store the ones defined in the model.
            if assign_to not in vertex_attributes:
                vertex_attributes[assign_to] = {}

            # Now, assign the given key-value attributes for the
            # vertex.
            vertex_attributes[assign_to][key] = value

        for line in ast:
            expression = line.expression
            if expression is None:
                continue

            match line.expression_type:
                case "set_types":
                    # For each vertex in the list, set the type key in
                    # vertex_types. If this key does not exist when the vertex
                    # is built - after processing the file - then that vertex
                    # will be considered undefined (and therefore invalid).
                    for vertex_name in expression.vertexList:
                        vertex_types[vertex_name] = expression.type

                case "set_edges":
                    is_conjunction = len(expression.vertexList1) > 1

                    # Check the RHS vertices and set the 'description' property
                    # on them, if it was specified.
                    for vertex_name in expression.vertexList2:
                        # Check that the RHS vertex has already been defined.
                        if vertex_name not in vertex_types:
                            self.__handle_missing_vertex(vertex_name, line,
                                                         controller=self.controller,
                                                         input_source_name=input_source_name)

                        # Set the description on them if specified.
                        if expression.description is not None:
                            # Actually assign the attribute.
                            # Delegated to a function to handle initialization of
                            # the dictionary entry consistently.
                            assign_vertex_attribute(vertex_name, 'description', expression.description)

                        # Create an entry for it in vertex_edges, if there
                        # isn't one.
                        if vertex_name not in vertex_edges:
                            vertex_edges[vertex_name] = []

                        # If we have a conjunction on the LHS, we need to generate
                        # a group ID for the RHS vertices. So make sure the group
                        # counter is initialized for each RHS vertex.
                        if vertex_name not in group_counter:
                            group_counter[vertex_name] = 0

                    # All vertices on the LHS are dependencies for the RHS, so
                    # loop over each one, creating an edge with each RHS -
                    # where the RHS is the 'owner' of the incident edges with
                    # its dependencies on the LHS.
                    for vertex_name in expression.vertexList1:
                        # Check that the LHS vertex has already been defined.
                        if vertex_name not in vertex_types:
                            self.__handle_missing_vertex(vertex_name, line,
                                                         controller=self.controller,
                                                         input_source_name=input_source_name)

                        for dependent_vertex_name in expression.vertexList2:
                            # We know dependent_vertex_name has an entry in
                            # vertex_edges.

                            # Process the arrow.
                            arrow = SimpleNamespace(
                                type=expression.link.linkType,
                                label=expression.link.label
                            )

                            # If the link type is = (i.e., the first character
                            # of the arrow is =, overwrite the arrow's label
                            # with rec).
                            # If the link type is = but a label is specified,
                            # overwrite the arrow's label with rec and append
                            # the label to the end of the label (with a comma
                            # delimiter).
                            if arrow.type == '=':
                                if arrow.label is None:
                                    arrow.label = 'rec'
                                else:
                                    arrow.label = f'rec,{(arrow.label or "").replace("=", "")}'

                            # Similarly to the above, if an arrow type is
                            # located in macros, just set the label to it, but
                            # if more flexibility is needed, this can be
                            # trivially modified.
                            if arrow.type != '-' and arrow.type != '=' and arrow.type in macros:
                                arrow.label = macros[arrow.type]

                            # Add the vertex edges to the dictionary.
                            vertex_edges[dependent_vertex_name].append(VertexEdge(
                                vertex_name,
                                label=arrow.label,
                                group_id=group_counter[dependent_vertex_name],
                                unique_group_id=unique_group_counter,
                                is_conjunction=is_conjunction
                            ))

                    # Having processed the edges, we can now increment the
                    # group counter for each RHS vertex if there was a conjunction
                    # on the LHS.
                    unique_group_counter += 1

                    for vertex_name in expression.vertexList2:
                        group_counter[vertex_name] += 1

                case "set_attributes":
                    # Set attributes for each vertex. Presently, this is just
                    # kept for when the vertexes are created and can be ignored
                    # but a more strict semantic model for the language could
                    # enforce that a vertex is defined as a type before
                    # attributes for that vertex can be defined.
                    # (vertex_types serves as the source of truth for the set
                    # of vertices for a given model).
                    for vertex_name in expression.vertexList:
                        if vertex_name not in vertex_types:
                            self.__handle_missing_vertex(vertex_name, line,
                                                         controller=self.controller,
                                                         input_source_name=input_source_name)

                        # Actually assign the attribute.
                        # Delegated to a function to handle initialization of
                        # the dictionary entry consistently.
                        assign_vertex_attribute(vertex_name, expression.key, expression.value)

                case "macro":
                    # Macros are simply stored and used later with set_types
                    # to resolve an arrow label.
                    macros[line.expression.symbol] = expression.substitution

                case _:
                    # Display a warning for an unrecognized expression.
                    self.controller.logger.warning(
                        f"Unrecognized expression type on line {line.parseinfo.line} "
                        f"in model: {line.expression_type}"
                    )

        # Loop over all the vertices, as noted above, vertex_types is the
        # source of truth for which vertices are to be registered. Then,
        # initialize the graph.
        known_vertices: dict[str, Vertex] = {}

        # Collect the information gathered from the AST into Vertex objects,
        # and store the resolved Vertex objects in known_vertices.
        for vertex_name in vertex_types:
            # Normalize the vertex attributes and edges (check if there are any).
            attributes = vertex_attributes[vertex_name] if vertex_name in vertex_attributes else None
            edges = vertex_edges[vertex_name] if vertex_name in vertex_edges else None

            # Initialize the Vertex object with the known type and assign the
            # attributes to it.
            known_vertices[vertex_name] = Vertex(vertex_name,
                                                 vertex_type=vertex_types[vertex_name],
                                                 edges=edges,
                                                 attributes=attributes)

        # Now process the edges for each vertex. (They need to be 'hydrated' as
        # they're currently just storing string references instead of
        # references to Vertex objects).
        for vertex_name, vertex in known_vertices.items():
            # Process the vertex edges (if there are any).
            # VertexEdge objects need to be created for each of the
            # dependencies. We know that the dependencies for the RHS are
            # placed on the LHS when edges are created.
            for edge in vertex.edges:
                if isinstance(edge.dependency, str):
                    edge.dependency = known_vertices[edge.dependency]

        # If we're in debug mode print everything we've found with Unicode box
        # characters for quick visual inspection.
        if self.controller.debug:
            for vertex in known_vertices.values():
                self.controller.logger.debug(f"Vertex :: {vertex}")

                for edge in vertex.edges:
                    draw_char = '  ├' if edge is not vertex.edges[-1] else '  └'
                    self.controller.logger.debug(f"{draw_char}── requires :: {edge}")

        # Insert the known_vertices into a Graph object and return it. Though
        # known_vertices is a list, the constructor for Graph will accept this
        # and automatically convert it into a dictionary.
        return Graph(known_vertices)

    @staticmethod
    def __handle_missing_vertex(name: str,
                                line=None,
                                controller: AbstractController = None,
                                input_source_name: str = 'unknown') -> None:
        if line is not None and hasattr(line, 'parseinfo') and line.parseinfo is not None:
            description_context = f'Error on line {line.parseinfo.line + 1} (pos. {line.parseinfo.pos + 1}).\n'
        else:
            description_context = f'Error whilst processing requested model.\n'

        raise InvalidModelData(
            description=f'{description_context}{name} used before declaration.',
            controller=controller,
            input_source=input_source_name,
        ).with_traceback(None) from None
