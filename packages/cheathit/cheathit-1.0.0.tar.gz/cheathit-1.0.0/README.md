# CheatHit: plagiarism detection tool for programming assignments

## Installation<a id="installation"></a>

Install [Python](https://www.python.org/downloads/) 3.9 or higher, then run:

```bash
pip install cheathit
```

## Usage<a id="usage"></a>

### Running<a id="running"></a>

Run CheatHit as follows:

```bash
cheathit /submission/directory
```

Or with [parameters](#parameters):

```bash
cheathit /submission/directory --path=group/student/problem/attempt --min-ngram=3 --max-ngram=10 --min-ratio=0.5 --max-clique=4
```

Or, if you want to save results to a file:

```bash
cheathit /submission/directory > /path/to/file
```

### Parameters<a id="parameters"></a>

#### `--path`<a id="path"></a>

Specify the structure of the submission directory with this parameter. Use the `student`, `group`, `problem`, and `attempt` sections separated with slashes, e.g.,  `group/group/student/problem/problem/attempt`. Each subsequent section gets CheatHit one level down the directory tree; the last level must be a file containing the submission.

- `student` corresponds to the set of programs submitted by an individual student;
- `group` corresponds to a group of students such that cheating is likely to take place within such a group (e.g., a school class);
- `problem` corresponds to a separate task shared by the students;
- `attempt` corresponds to a separate submission of a student.

The `student` section is required (i.e., there should be at least one of these in `--path`); the other three sections are optional. If the same section appears in `--path` multiple times, CheatHit will simply concatenate its values to obtain the “true” representation of the section.

The default value of `--path` is `student`, which is suitable for cases when there is a single directory with many files, one file per student.

#### `--min-ngram`<a id="min-ngram"></a>

Minimum ngram size (number of consecutive [tokens](#tokenization)) to analyze across the submissions.

The default value of `--min-ngram` is `1`.

#### `--max-ngram`<a id="max-ngram"></a>

Maximum ngram size (number of consecutive [tokens](#tokenization)) to analyze across the submissions.

The default value of `--max-ngram` is `20`.

#### `--min-ratio`<a id="min-ratio"></a>

Minimum ratio of the number of [tokens](#tokenization) shared by two submissions to the number of tokens in the longer of the submissions required so that the pair is included in the report.

The default value of `--min-ratio` is `0.2`.

#### `--max-clique`<a id="max-clique"></a>

If an ngram (a sequence of [tokens](#tokenization)) occurs in submissions of more than `--max-clique` students (or in submissions of students from more than `--max-clique` groups), it is not considered distinctive.

The default value of `--max-clique` is:

- `2` if students are assigned groups ([`--path`](#path) includes `group`),
- `5` otherwise.

### Tokenization<a id="tokenization"></a>

CheatHit tokenizes source code into alphanumeric words (which can also contain underscores) and non-alphanumeric characters. Whitespace, semicolons, and commas are ignored. Two special markers, `<START>` and `<END>`, are added to the beginning and end of a token sequence. Hence,

```
CheatHit supports C++, Python v2 & v3, and _even_ VB.NET; awesome!
```

would be tokenized as

```
['<START>', 'CheatHit', 'supports', 'C', '+', '+', 'Python', 'v2', '&', 'v3', 'and', '_even_', 'VB', '.', 'NET', 'awesome', '!', '<END>']
```

### Results<a id="results"></a>

For each pair of students CheatHit will report how much code is shared between the students while adjusting for how distinctive the shared code is. See the [Parameters](#parameters) and [Tokenization](#tokenization) sections above for an insight into what CheatHit considers distinctive.
