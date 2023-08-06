![](logo.png)

# Jaypeg

A command line tool for converting and resizing image files.
Jaypeg converts an entire folder of images files to jpeg.  It also lets you resize the files so that they load quickly on the web. 

Jaypeg relies on `filetype` to detect filetypes and `pillow` to resize and convert the images. Gif and Tiff files are converted to jpg. Jpeg files are resized. Other image formats such as Png or Webp are not changed (but could be in future versions).  

## installation 

`pip install jaypeg` 

## usage 

`$ jaypeg folder/of/files`  
will convert any gif or tiff file to jpg
will resize files to 2MB or less by default  
files are updated in their current location

save altered files in a new directory 
`$ jaypeg folder/of/files --out-path new/folder`  

set the file size limit (ex. 4MB). All files larger than the limit will be resized to be smaller than the limit.
`$ jaypeg folder/of/files --size 4000000`

Arguments:
  PATH  [required]

Options:
  --size INTEGER        [default: 2000000]
  --out-path TEXT
  --install-completion  Install completion for the current shell.
  --show-completion     Show completion for the current shell, to copy it or
                        customize the installation.
  --help                Show this message and exit.

## license 

Copyright 2022 Andrew Paul Janco

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.