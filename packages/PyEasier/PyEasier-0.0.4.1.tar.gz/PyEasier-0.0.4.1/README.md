# PyEasier

This python package is made with the soul content of
making python have less boilerplate code. You may be 
wondering how to use this helpful python package
well my favorite coder it is rather simple look 
bellow for a list of commands and what they do.



IF YOU FIND A BUG REPORT IT HERE: [_**CLICK ME**_](https://github.com/YellowBoyYams/PyEasier/issues)

1. RanNum(low, high)<br/>
This function helps you get a random whole number.
The low and high parameters are there for you to
put in the highest number and lowest number of the range then the 
function will choose a random number in that range.

``
print(RanNum(0, 100))
``<br/>
Console Output:<br/>
``77``<br>
2. RanFloat(low, high)<br/>
This function helps you get a random decimal number.
The low and high parameters are there for you to put
in the highest number and the lowest number of the range then the function will choose a random decimal number
inside that range.<br>
``
print(RanFloat(0, 100))
``<br/>
Console Output:<br/>
``42.012440655242365``<br>
3. cap(num, decimalPlaces)<br/>
This function helps you make a decimal number shorter.<br>
``
print(cap(42.012440655242365, 2))
``<br/>
Console Output:<br/>
``42.01``<br>
4. package(module)<br>
This function helps you run pip commands through code.<br>
``
package("pyeasier")
``<br/>
Console Output:<br/>
``Collecting PyEasier
  Downloading PyEasier-py3-none-any.whl (2.5 kB)
Requirement already satisfied: py2app in ./venv/lib/python3.9/site-packages (from PyEasier) (0.28.2)
Requirement already satisfied: pyinstaller in ./venv/lib/python3.9/site-packages (from PyEasier) (5.1)
Requirement already satisfied: macholib>=1.16 in ./venv/lib/python3.9/site-packages (from py2app->PyEasier) (1.16)
Requirement already satisfied: modulegraph>=0.17 in ./venv/lib/python3.9/site-packages (from py2app->PyEasier) (0.19.2)
Requirement already satisfied: altgraph>=0.16 in ./venv/lib/python3.9/site-packages (from py2app->PyEasier) (0.17.2)
Requirement already satisfied: pyinstaller-hooks-contrib>=2021.4 in ./venv/lib/python3.9/site-packages (from pyinstaller->PyEasier) (2022.7)
Requirement already satisfied: setuptools in ./venv/lib/python3.9/site-packages (from pyinstaller->PyEasier) (60.2.0)
Installing collected packages: PyEasier
Successfully installed PyEasier
``<br>
5. runCmd(cmd)<br>
This function allows you to run terminal commands through code instead of you having to go to the terminal/command prompt and running the command there.<br>
``
runCmd("pip install pyeasier")
``<br/>
Console Output:<br/>
``Collecting PyEasier
  Downloading PyEasier-py3-none-any.whl (2.5 kB)
Requirement already satisfied: py2app in ./venv/lib/python3.9/site-packages (from PyEasier) (0.28.2)
Requirement already satisfied: pyinstaller in ./venv/lib/python3.9/site-packages (from PyEasier) (5.1)
Requirement already satisfied: macholib>=1.16 in ./venv/lib/python3.9/site-packages (from py2app->PyEasier) (1.16)
Requirement already satisfied: modulegraph>=0.17 in ./venv/lib/python3.9/site-packages (from py2app->PyEasier) (0.19.2)
Requirement already satisfied: altgraph>=0.16 in ./venv/lib/python3.9/site-packages (from py2app->PyEasier) (0.17.2)
Requirement already satisfied: pyinstaller-hooks-contrib>=2021.4 in ./venv/lib/python3.9/site-packages (from pyinstaller->PyEasier) (2022.7)
Requirement already satisfied: setuptools in ./venv/lib/python3.9/site-packages (from pyinstaller->PyEasier) (60.2.0)
Installing collected packages: PyEasier
Successfully installed PyEasier``<br>
6. osName()
This function allows you to get the os name of the user.<br>
``
osName()
``<br/>
Console Output:<br/>
``Darwin``<br>
7. py2dmg(fileName, iconFile(optional))
This function allows you to package your code into a dmg file for Mac users.<br>
``
py2dmg("myCoolGame.py", iconFile = "rick.icn")
``<br/>
Console Output:<br/>
``
The console output is too long to put here
``<br>
8. py2exe(filename, console(Optional), iconFileName(Optional))
This function maybe buggy please let me know if it has bugs because I am on a Mac and can't test this out.
This function helps you with packaging your code into an exe file for Window Users. If you want a gui program you don't need to set 
console to False it is set by default but if you have a terminal game, and you need the console then set console to true.<br>

``
py2exe("myCoolGame.py", console = False, iconFile = "rick.icn")
``<br/>
Console Output:
<br/>
``The console output is too long to put here too``<br>


9. write(file, text)
This function helps you write into files.<br>

``
write(nice.py, "Hi")
``<br/>

Console Output:
<br/>
``
Nothing to put here
``<br>
10. read(file, mode(Optional))
This function helps you read files. By default, the mode is set to t but if you need to read images and media files set the mode to b.<br>
``
write(nice.py, "Hi")<br>
r = read(nice.py, mode = "t")<br>
print(r[0])<br>
``<br>
Console Output:<br/>
``
Hi
``<br>
11. append(filename, text)
This function helps you append text to a file.<br>
``
write(nice.py, "H")<br>
append(nice.py, "e")<br>
r = read(nice.py, mode = "t")<br>
print(r[0])
``<br>
Console Output:<br>
``
He
``<br>
12. create(filename)
This function helps you create a new file in your directory.<br>
``
create("nice.py")<br>
write(nice.py, "H")<br>
append(nice.py, "e")<br>
r = read(nice.py, mode = "t")<br>
print(r[0])
``<br>
Console Output:
<br>
``
He
``