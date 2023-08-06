import typer
from typing import Optional
import os
import filetype
from PIL import Image
from pathlib import Path

#This section changes the size of an image file if it is larger than a given size
#https://stackoverflow.com/questions/13407717/python-image-library-pil-how-to-compress-image-into-desired-file-size
class file_counter(object):
    def __init__(self):
        self.position = self.size = 0

    def seek(self, offset, whence=0):
        if whence == 1:
            offset += self.position
        elif whence == 2:
            offset += self.size
        self.position = min(offset, self.size)

    def tell(self):
        return self.position

    def write(self, string):
        self.position += len(string)
        self.size = max(self.size, self.position)

def smaller_than(im, size, guess=70, subsampling=1, low=1, high=100):
    while low < high:
        counter = file_counter()
        im.save(counter, format='JPEG', subsampling=subsampling, quality=guess)
        if counter.size < size:
            low = guess
        else:
            high = guess - 1
        guess = (low + high + 1) // 2
    return low

def is_image(file):
    """Leaves the png and webp alone"""
    kind = filetype.guess(str(file))
    if kind.mime == 'image/jpeg':
        return True

    elif kind.mime == 'image/gif':
        im = Image.open(str(file))
        im = im.convert('RGB')
        im.save(str(file), "JPEG", quality=100)
        return True

    elif kind.mime == 'image/tiff':
        im = Image.open(str(file))
        im = im.convert("RGB")
        im.save(str(file), "JPEG", quality=100)
        return True

    else:
        return False

def change_size_if_needed(file:Path, size:int, out_path:str):
    if is_image(file):
        if os.path.getsize(str(file)) > size:
            message = typer.style(f'resizing: {file}', fg=typer.colors.GREEN, bold=True)
            typer.echo(message)
            
            im = Image.open(file)
            size = smaller_than(im, size)
            if out_path:
                im.save((out_path / file.name), 'JPEG', quality=size)
            else:
                im.save(file, 'JPEG', quality=size)
        else:
            message = typer.style(f'keeping: {file}', fg=typer.colors.WHITE, bold=True)
            typer.echo(message)

def main(path: str, size:int=2000000, out_path:Optional[str]=None):
    """ 
    Convert a directory of image files to jpeg and 
    resize them (2MB by default)
    """
    for file in Path(path).rglob("*"):
        change_size_if_needed(file, size, out_path)
    

if __name__ == "__main__":
    typer.run(main)
