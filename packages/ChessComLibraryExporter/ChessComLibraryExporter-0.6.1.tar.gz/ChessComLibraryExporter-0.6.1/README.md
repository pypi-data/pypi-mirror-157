# Chess.com Library Exporter

A command line utility that uses Selenium (Chess.com please improve API support!) to help you download your entire archive of games in `chess.com/library`.


## Usage

**From PyPI:**

```bash
$ pip install ChessComLibraryExporter
$ chess_library_exporter
Username: manuelpepe
Password: 

Found 6 collections
...
```

**From source:**

```bash
$ git clone https://github.com/manuelpepe/ChessComLibraryExporter
$ cd ChessComLibraryExporter
$ pip install -r requirements.txt
$ python chess_library_exporter.py
Username: manuelpepe
Password: 

Found 6 collections
...
```


By default, your library will be exported to a `library/` directory in your current working directory.
You can change it with the `-o path/to/directory` parameter. 

## Support

Firefox and Chrome are supported (use `-b firefox` or `-b chrome`, defaults to firefox). Headless mode can also be deactivated with the `-H` flag (Headless mode seems to break on Chrome).
