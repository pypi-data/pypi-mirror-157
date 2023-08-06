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
``77``<br><br>
2. RanFloat(low, high)<br/>
This function helps you get a random decimal number.
The low and high parameters are there for you to put
in the highest number and the lowest number of the range then the function will choose a random decimal number
inside that range.<br>
``
print(RanFloat(0, 100))
``<br/>
Console Output:<br/>
``42.012440655242365``<br><br>
3. cap(num, decimalPlaces)<br/>
This function helps you make a decimal number shorter.<br>
``
print(cap(42.012440655242365, 2))
``<br/>
Console Output:<br/>
``42.01``<br><br>
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
``<br><br>
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
Successfully installed PyEasier``<br><br>
6. osName()<br>
This function allows you to get the os name of the user.<br>
``
osName()
``<br/>
Console Output:<br/>
``Darwin``<br><br>
7. py2dmg(fileName)<br>
This function allows you to package your code into a dmg file for Mac users.<br>
``
py2dmg("myCoolGame.py")
``<br/>
Console Output:<br/>
``
The console output is too long to put here
``<br><br>
8. py2exe(filename, console(Optional), iconFileName(Optional))<br>
This function maybe buggy please let me know if it has bugs because I am on a Mac and can't test this out.
This function helps you with packaging your code into an exe file for Window Users. If you want a gui program you don't need to set 
console to False it is set by default but if you have a terminal game, and you need the console then set console to true.<br>

``
py2exe("myCoolGame.py", console = False, iconFile = "rick.icn")
``<br/>
Console Output:
<br/>
``The console output is too long to put here too``<br><br>

9. write(file, text)<br>
This function helps you write into files.<br>

``
write(nice.py, "Hi")
``<br/>

Console Output:
<br/>
``
Nothing to put here
``<br><br>
10. read(file, mode(Optional))<br>
This function helps you read files. By default, the mode is set to t but if you need to read images and media files set the mode to b.<br>
``
write(nice.py, "Hi")``<br>``
r = read(nice.py, mode = "t")``<br>``
print(r[0])
``<br>
Console Output:<br/>
``
Hi
``<br><br>
11. append(filename, text)<br>
This function helps you append text to a file.<br>
``
write(nice.py, "H")``<br>``
append(nice.py, "e")``<br>``
r = read(nice.py, mode = "t")``<br>``
print(r[0])
``<br>
Console Output:<br>
``
He
``<br><br>
12. create(filename)<br>
This function helps you create a new file in your directory.<br>
``
create("nice.py")``<br>``
write(nice.py, "H")``<br>``
append(nice.py, "e")``<br>``
r = read(nice.py, mode = "t")``<br>``
print(r[0])``
<br>
Console Output:
<br>
``He``<br><br>
13. cos(num)<br>
This functions helps you get the cosine of the number that you input.<br>
``
print(cos(1))
``<br>
Console Output:
<br>
``0.5403023058681398``<br><br>
14. sin(num)<br>
This function helps you get the sine of the number that you input.<br>
``
print(sin(1))
``<br>
Console Output:
<br>
``0.8414709848078965``
15. delete(filename)<br>
This function helps you delete the file that you input.<br>
``
delete("nice.py")
``<br>
Console Output:
<br>
``✨ Deleted nice.py ✨``<br><br>
16. log(num, base)<br>
This function helps you find the logarithm of the number that you entered to the base that you entered.<br>
``
print(log(10, 2))
``<br>
Console Output:
<br>
``3.3219280948873626``<br><br>
17. tan(num)<br>
This function helps you find the tangent of the number that you entered.<br>
``print(tan(1))``<br>
Console Output:
<br>
``1.557407724654902``<br><br>
18. asin(num)<br>
This function helps you find the arc-sine of the number that you input.<br>
``print(asin(1))``<br>
Console Output:
<br>
``1.5707963267948966``<br><br>
19. acos(num)<br>
This function helps you find the arc-cosine of the number that you input.<br>
``print(acos(1))``<br>
Console Output:
<br>
``0.0``<br><br>
20. getBatteryLevel()<br>
This function gives you the battery of the user's device.<br>
``print(f'{getBatteryLevel()}%')``<br>
Console Output:
<br>
``66%``<br><br>
21. isPluggedIn()<br>
This function gives you either true or false if the user's device is plugged in.<br>
``print(isPluggedIn())``<br>
Console Output:
<br>
``False``<br><br>
22. findCircumference(radius)<br>
This function helps you calculate the circumference of a circle.<br>
``print(findCircumference(1))``<br>
Console Output:
<br>
``6.283184``<br><br>
23. findRadius(circumference)<br>
This function helps you find the radius of a circle.<br>
``print(findRadius(6.283184))``<br>
Console Output:
<br>
``1``<br><br>
24. findDiameter(radius)<br>
This function helps you find the diameter of a circle.<br>
``print(findDiameter(1))``<br>
Console Output:
<br>
``2``<br><br>
25. technoblade()<br>
This function pays tribute the youtuber Technoblade.<br>
``technoblade()``<br>
Console Output:
<br>
``🐷😞Rip Techno you will be missed 😞🐷``<br><br>
-YellowYams(Vedic Mukherjee)
