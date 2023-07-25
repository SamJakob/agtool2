<div style="text-align: center;">
  <a href="https://github.com/SamJakob/agtool2">
    <img src="./docs-gen/logo.svg" alt="agtool logo" width="484" />
  </a>
</div>

# agtool
`agtool` (account/access graphs tool) is a tool to visualize, compute and
transform account access graphs based on an input specification.

## Scripts
- Build documentation: `make docs`
  - By default, this opens the browser. To avoid this, use `make docs:silent`.

## Dependencies
- For Python dependencies, see `requirements.txt`, these can be installed with
`pip install -r requirements.txt`.

## Running

### macOS and Linux
- Either run `./bin/agtool` directly in the Terminal. (You may need to
`chmod +x ./bin/agtool` first) - this has the limitation of only being able to
be executed from the project root.
- Alternatively, add `export PATH="<path to agtool>/bin/agtool:$PATH"` to your
`rc` file (either `~/.bashrc` or `~/.zshrc` depending on whether you use bash
or zsh respectively - you can check with `echo $0`).

### Windows
- Either run `.\bin\agtool.bat` directly in Windows Terminal (or Command
Prompt / PowerShell).
- Alternatively, press the Start button and type in "Edit environment variables
for your account" (or "Edit the system environment variables") and add the
`bin` folder to either your user's `Path` environment variable or the system's
`PATH` environment variable.

## Code Structure
- Module information such as version information, module documentation, etc.,
is stored in `app/__init__.py`.
- The main executable file is `app/__main__.py` which fetches the basic command 
  arguments and passes them to `app/cli` which serves as the main component and
  entry point of the CLI 'form factor' of the application.
