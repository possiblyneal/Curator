# Curator

Curates your perfect MAME collection based on your preferences. While it runs in the terminal, it is made to be easy to understand and use! Lots of explanation is provided at request along the way. It uses the MAME internal database, plus additional files to create filterable attributes for each game. Rebuilder is used to build your collection from source folders.

## Capabilities:

- Excellent clone handling options. Choose best rom variation based on number of players and language. Can prefer US releases.
- Many different filters:
  - Year
  - Genre/ Category
  - Language
  - Control Types
- Easily eliminate non-games and screenless games.
- Includes only the samples you need.
- Keep latest prototype for unreleased games.
- Optionally recompress in 7z for smaller file sizes.

## Known Issues:

- Year filtering doesn't account for incomplete MAME database entries (i.e. 198?, 19??, etc.) These games will be discarded. It requires more investigation, but I believe this is typically found on hacks, bootlegs, and prototypes so it is likely inconsequential for most scenarios.
- Please share any you find!

## Future Upgrades:

- Auto download helper files.
- Filter based on community game ratings
- Maybe a GUI – (amateur programmer here!)
- Please share any ideas you may have! However as a disclaimer, I'm not interested in supporting things without broad appeal or require the use of data sources that are not maintained or at risk of not being maintained in the near future. That would include most new projects.

## Helper Files (or additional required files):

- Weblinks are provided for all the download locations for the following:
  - Rebuilder
  - ini
  - Catver.ini
