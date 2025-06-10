# Book Name Normalization Rule

All user input and code that references Bible books must normalize the book name to the database abbreviation before querying or writing to the database.

## Rationale
- Prevents missing data due to mismatches between user input (e.g., 'John') and database abbreviations (e.g., 'Jhn').
- Ensures all queries and features work regardless of input format.
- Avoids silent data loss and confusion in API/UI.

## Implementation
- Use the mapping in `src/dspy_programs/contextual_insights_program.py` (BOOK_NAME_TO_ABBR).
- All queries must call `normalize_book_name(book)` or, preferably, the `parse_reference(reference)` utility before using book names in SQL or ORM queries.
- The mapping table is also documented in the project README.
- The `parse_reference` utility returns the normalized abbreviation, chapter, and verse for robust, consistent queries.

## Mapping Table
| Canonical Name      | Abbreviation |
|---------------------|--------------|
| Genesis             | Gen          |
| Exodus              | Exo          |
| Leviticus           | Lev          |
| Numbers             | Num          |
| Deuteronomy         | Deu          |
| Joshua              | Jos          |
| Judges              | Jdg          |
| Ruth                | Rut          |
| 1 Samuel            | 1Sa          |
| 2 Samuel            | 2Sa          |
| 1 Kings             | 1Ki          |
| 2 Kings             | 2Ki          |
| 1 Chronicles        | 1Ch          |
| 2 Chronicles        | 2Ch          |
| Ezra                | Ezr          |
| Nehemiah            | Neh          |
| Esther              | Est          |
| Job                 | Job          |
| Psalms              | Psa          |
| Proverbs            | Pro          |
| Ecclesiastes        | Ecc          |
| Song of Solomon     | Sng          |
| Isaiah              | Isa          |
| Jeremiah            | Jer          |
| Lamentations        | Lam          |
| Ezekiel             | Ezk          |
| Daniel              | Dan          |
| Hosea               | Hos          |
| Joel                | Joe          |
| Amos                | Amo          |
| Obadiah             | Oba          |
| Jonah               | Jon          |
| Micah               | Mic          |
| Nahum               | Nah          |
| Habakkuk            | Hab          |
| Zephaniah           | Zep          |
| Haggai              | Hag          |
| Zechariah           | Zec          |
| Malachi             | Mal          |
| Matthew             | Mat          |
| Mark                | Mrk          |
| Luke                | Luk          |
| John                | Jhn          |
| Acts                | Act          |
| Romans              | Rom          |
| 1 Corinthians       | 1Co          |
| 2 Corinthians       | 2Co          |
| Galatians           | Gal          |
| Ephesians           | Eph          |
| Philippians         | Php          |
| Colossians          | Col          |
| 1 Thessalonians     | 1Th          |
| 2 Thessalonians     | 2Th          |
| 1 Timothy           | 1Ti          |
| 2 Timothy           | 2Ti          |
| Titus               | Tit          |
| Philemon            | Phm          |
| Hebrews             | Heb          |
| James               | Jas          |
| 1 Peter             | 1Pe          |
| 2 Peter             | 2Pe          |
| 1 John              | 1Jn          |
| 2 John              | 2Jn          |
| 3 John              | 3Jn          |
| Jude                | Jud          |
| Revelation          | Rev          |

## Enforcement
- All new code and major edits must use this normalization.
- All DB queries must use the `parse_reference` utility to extract the normalized abbreviation, chapter, and verse.
- Reviewers must check for direct use of book names in queries and require normalization.
- This is enforced in code and tested in integration tests.

---
**Note:** The `parse_reference` utility is defined in `src/dspy_programs/contextual_insights_program.py` and should be used for all reference parsing and normalization. 