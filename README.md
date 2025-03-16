**This repo is a demo.  Do not use.  See the Purpose & Credits section at the bottom.**

# EPS to PNG Converter

A simple EPS (Encapsulated PostScript) to PNG converter written in Python using only standard library modules.

## Features

- Parse and interpret basic PostScript commands from EPS files
- Convert EPS graphics to PNG format
- Supports common drawing operations:
  - Lines and paths
  - Basic shapes (rectangles, triangles, polygons)
  - Arcs and circles
  - Filling and stroking paths
  - Grayscale color
- Optimized PNG output with zlib compression
- Option to disable compression

## Limitations

- Limited subset of PostScript commands supported
- No support for text or complex transformations
- Grayscale only (no RGB color)
- No anti-aliasing

## Usage

```bash
# Basic usage with compression (default)
python eps_to_png.py input.eps output.png

# Disable compression (for debugging or comparison)
python eps_to_png.py input.eps output.png --no-compress
```

## How It Works

1. **EPS Parser**: Extracts bounding box and commands from the EPS file
2. **PostScript Interpreter**: Processes commands and builds a bitmap representation
3. **PNG Encoder**: Encodes the bitmap as a PNG file with zlib compression

## Example Output

The repository includes several test EPS files:

- `test_square.eps` - Simple square with a diagonal line
- `test_shapes.eps` - Various polygons with different fill colors
- `test_circles.eps` - Circles and arcs demonstrating curve support
- `test_solid.eps` - Solid color areas that compress efficiently
- `test_commands.eps` - Various PostScript commands demonstration

## Implementation Details

The converter consists of three main components:

1. **Bitmap Class**: Provides methods for drawing lines, shapes, and filling polygons
2. **PostScript Interpreter**: Implements a stack-based interpreter for basic PostScript commands
3. **PNG Encoder**: Creates a valid PNG file with zlib-compressed data

## Compression

The converter uses the Python standard library's `zlib` module to compress the PNG image data. This can significantly reduce file sizes:

| Image            | Uncompressed Size | Compressed Size | Reduction |
|------------------|-------------------|----------------|-----------|
| test_circles.png | 90,373 bytes      | 1,563 bytes    | 98.3%     |
| test_solid.png   | 40,268 bytes      | 246 bytes      | 99.4%     |

## Future Improvements

Potential enhancements:
- Support for more PostScript commands
- RGB color support
- Basic text rendering
- Proper transformation support (scale, rotate, translate)
- Adaptive filtering to improve compression

# Purpose & Credits

All of the code in this repository and the entire README.md text above this section was authored by [Anthropic](https://www.anthropic.com/)'s [Claude Code research preview](https://docs.anthropic.com/en/docs/agents-and-tools/claude-code/overview) 0.2.32 which used Claude Sonnet 3.7.

Before starting, I created the simple [CLAUDE.md](CLAUDE.md) file for it to use by default as guidance.  The directory was otherwise empty.

## Why?

Al Sweigart tried to troll people into doing this by offering a "Prove me wrong" challenge.

_"""AI is completely unable to generate a Python function that converts a .eps file to a .png file without using a third-party package. It can't write the code to do it directly even though both formats are well-known. This is a straightforward task with fairly well-specified requirements, but AI is completely unable to do it. Prove me wrong."""_

Others have already covered how that statement isn't correct in numerous ways.  But ignoring all of that, it serves as an interesting little project demo of readily available AI capabilities in March 2025.

The response from `claude` CLI myself upon my first prompt (see the section below) basically agrees with people commenting on this as problem:

```
● To convert .eps to .png without third-party packages, I'd need to:

  1. Parse the EPS file format (PostScript subset)
  2. Implement a PostScript interpreter
  3. Render the graphics commands to a bitmap
  4. Encode the bitmap as PNG

  This is extremely complex without libraries. PostScript is a full programming language and PNG requires compression algorithms. Would you
   consider allowing just one library like Pillow, or shall I research the raw file formats?
```

That's claude speak for "WTF! Are you *really* gonna make me do this when the tool you need is right there?" AKA the "what am I? a farmer?" meme.

I will note that it did not seem to realize while composing that reponse that the compression algorithms aren't actually required and that the zlib module in the standard library is not third party and provides them. I had it use that later and it nailed it.


## Prompts

The prompts I gave the `claude` CLI, in sequence, were:

* "We want to write a new tool in Python today that converts a .eps file (input) to a .png file (output).  Ultimately without using any third party packages.  Can you draft a plan for how you'd go about this task and what you would need?"
* "Lets use the raw file formats.  We don't need a 100% solution, we can constrain the specifics of both what the input can contain and use the simplest form of png output.",
* "yes please. and if you are unable to research something on your own, just ask me and i can go find the information for you.",
* "I have downloaded an EPS spec and placed it in the `5002.EPSF_Spec.pdf` file.",
   * _I saved a local copy of https://web.archive.org/web/20170818010030/http://wwwimages.adobe.com/content/dam/Adobe/en/devnet/postscript/pdfs/5002.EPSF_Spec.pdf that https://en.wikipedia.org/wiki/Encapsulated_PostScript linked to for it to use._
* "i've made a simpler text only version of that doc, look in the `EPSF-html` directory.",
   * _I ran the above pdf through pdftohtml (not installed on the machine I was running `claude` on -- Or I likely could've just told Claude to use the tool to make the desired low token count text version of the spec)_
* "lets keep it simple and skip antialiasing and color support. for the PNG we can skip compression (use type 0). look at the `PostScript Tutorial.html` file for basic postscript understanding.",
   * _I saved and gave it a copy of https://paulbourke.net/dataformats/postscript/ for it to use if desired._
* "sounds great, lets implement that.",
* "For test purposes to validate our work, lets allow the use of third party libraries in test code. Can you write a unittest that uses relevant libraries or external tools to check the test data inputs and outputs?",
* "Lets create a local virtual environment (venv) to install requirements within to execute these.",
* "/cost ",
   * \
```
  ⎿  Total cost:            $1.75
     Total code changes:    1191 lines added, 11 lines removed
```
* "run test_eps_to_png and debug what's going on",
   * _Claude hadn't run all of the tests it had generated but thought it was done, here's me prodding it..._
* "when i look at test_circles.png it is a blank black image",
   * _This was after me visually inspecting the png's generated from its test files._*
* "do our unittests check for different pixel values in relevant places in the final png image?",
   * _Another hint as the changes it made still hadn't actually made good PNGs despite potentially fixing one issue Claude found._
* "we don't want to allow use of third party libraries in our actual utility, only in the tests.  was pillow compressing its png files?  our code should not (for simplicity).  i've added a PNG spec in `rfc2083.txt` if you want it.",
   * _Claude was asking for permission to add an alternate codepath using Pillow in the main utility for its debugging. I decided to be a stick in the mud on this point for the challenge._
* "great.  if you use the `zlib` library from the standard library, could you add png compression support?",
* "/cost ",
   * \
```
  ⎿  Total cost:            $5.97
     Total code changes:    1637 lines added, 251 lines removed
```

As usual, the bulk of development time|cost is final bit to get things working and tested. :P  I made zero edits to any source files or test inputs in this project.

## Lessons for myself, the human

1. In hindsight: I shouldn't have told to to skip compression as it looks like that ironically overcomplicated matters.  I'm also wondering if I should've just let it get ahead of itself and include antialiasing as it wanted to in its initial plan up front.  But that felt mean, no human would rationally choose to do that even though it's a very nerdsnipe worthy feature.
2. Providing a little more rules and structure ahead of time in [CLAUDE.md](CLAUDE.md) could help. I intentionally did not want to give it much beyond "Python" and "don't use third party libraries" just for fun. But some idea as to how things should be laid out out and my test suite invocation expectations and virtual env use expectations might've wound up with it helping itself and not forgetting to run some of its own tests requiring less prompting on my part.
3. Claude generated all of the test `.eps` inputs and test cases. I have no idea if those are even valid EPS! Or even how to validate them off the top of my head (LOL when do I _ever_ touch .eps files?!?).  But if I wanted to, I could just ask claude how... a Google search found https://jumpshare.com/viewer/eps which renders test_shapes.eps and test_circles.eps as our generated code did. Good sign!
4. I have not code reviewed anything generated here beyond having skimmed it as it was generated and thinking _"neat! this is along the lines of what I was expecting - I am okay with executing it"_.
5. Not specifying the interface or things like how to handle PNG resolutions was intentional. I wanted to see what it came up with. EPS as generally vector and PNG as bitmap it appears to have made a choice that greatly simplified its implementation. If we wanted dynamic PNG output sizes we'd need to ask for that... Good example of follow on work along with things like antialiasing and color support.
6. The most useful models for serious work today cost real $money.

## Why didn't I include the full Claude Code console log or a terminal screen capture video

Who's got time for that? (read: _someone else_ surely does) - It is interesting. But I think the most interesting thing you can do is to try this type of exercise for yourself. I realize raw list of prompts without the conversational replies from the model inbetween reads weird.

## Interesting tips for Claude Code CLI users

* You can ask `claude` to update its own CLAUDE.md file...  This may be similar to using /compact to free up context window space but persists for future runs.  Is this a form of long term project context long term memory?  _Maaybe?_  I'm excited to see this concept evolve.
* You will find yourself butting heads with context windows a lot on any reasonable size codebase and task.
   * Try to think of problems as you would yourself - you don't hold the context of all files and APIs in a project in your memory at all time, why should an LLM?  Information overload is real.
   * Searching around parts of files for relevant smaller pieces of context is natural and when you see `claude` doing this it is a good thing - that is also how I work when skipping around a codebase in our own development environment, including rereading documentation and code snippets at various times.
* Update CLAUDE.md yourself when you see particular behavior patterns you'd like it to avoid in the future.
* Treat your LLM as a junior colleague.  It won't be right all the time.  Neither will you!  Accept that and work with it.

