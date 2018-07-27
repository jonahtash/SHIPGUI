from pip._internal import main
from os import system

main(['install','--upgrade', 'pip', 'wheel', 'setuptools'])
main(['install','docutils', 'pygments', 'pypiwin32', 'kivy.deps.sdl2', 'kivy.deps.glew'])
main(['install', 'kivy.deps.angle'])
main(['install', 'kivy'])
main(['install', 'kivymd'])
system("garden install filebrowser")
