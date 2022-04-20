# Na používanie daj do main.py:
# from Ves import ves as vesClass
# 
# Na vytvorenie objektu zo stringu pouzi:
# vesOkjekt = vesClass(vesStr = nejakyTvojVesString)
# 
# Pre vratenie obrazku je to:
# obrazokVPamati = vesOkjekt.getImage(scale = kolkoKratZvacseny)
# Bez scale alebo scale = 1 obrazok vrati vo velkosti zadanej v riadku s VES
# Pre scale > 1 obrazok zvacsi a pre scale < 1 obrazok zmensi (vynasobi sirku a vysku so scale)
# Obrazok vrati ako BytesIO
# 
# Priklad na konci suboru pod if(__name__ == "__main__")...

from time import time
from PIL import Image
from os import remove
from io import BytesIO

class ves():
  class vesObject():
    def __init__(self, command, attributes):
      self.command = command
      self.attributes = attributes

  # All the convert functions are simple, not gonna say anything more than this
  def convertSize(self, size, scales):
    defWidth = scales[0]
    width = scales[2]
    return int(size * (width/defWidth))

  def convertPoint(self, point, scales):
    return (self.convertSize(point[0], scales), self.convertSize(point[1], scales))

  def drawPoints(self, points, colour):  # This function is used to draw rasterised objects, ignores anything outside the bounds of the image
    if(self.faster):
      points = list(set(points))   # Removes duplicates, *should* make rendering faster, from limited testing ~4x faster, especially with bigger images
    
    for point in points:
      if(point[0] < 0 or point[1] < 0 or point[0] >= self.image.width or point[1] >= self.image.height):
        pass
      else:
        self.image.putpixel(point, colour)


  def line(self, A, B): # Draws lines
    points = []
    if A[0] == B[0]:  # Case where the points are "on top of" one another
      if A[1] > B[1]:
        A,B = B,A
      for y in range(A[1], B[1] + 1):
        points.append((A[0], y))
    elif A[1] == B[1]:  # Case where the points are "next to" one another
      if A[0] > B[0]:
        A,B=B,A
      for x in range(A[0], B[0] + 1):
        points.append((x, A[1]))
    else: # All other cases
      if A[0] > B[0]:
        A,B=B,A 
      dx = B[0] - A[0] 
      dy = B[1] - A[1]
      k = dy/dx
      if abs(k) > 1:  # Angle of line more than 45 degrees
        for y in range(min(A[1], B[1]), max(A[1],B[1]) + 1):
          x = int((y - A[1] + (k) * A[0]) * (dx/dy))
          points.append((x,y))
      else: # Angle of line less than 45 degrees
        for x in range(min(A[0], B[0]), max(A[0], B[0])+ 1):
          y = int(k * (x - A[0]) + A[1])
          points.append((x,y))
    return points


  def circle(self, S, r): # Circle with 8 symetrical points
    points = []
    for x in range(int(r/(2**(1/2))+1)):
      y = int((r**2 - x**2)**(1/2))
      points.append((x + S[0], y + S[1]))
      points.append((y + S[0], x + S[1]))
      points.append((y + S[0], -x + S[1]))
      points.append((x + S[0], -y + S[1]))
      points.append((-x + S[0], y + S[1]))
      points.append((-x + S[0], -y + S[1]))
      points.append((-y + S[0], x + S[1]))
      points.append((-y + S[0], -x + S[1]))
    
    return points

  def filledCircle(self, S, r): # Same as above, but the inside is "painted" using lines  
    points = []
    for x in range(int(r/(2**(1/2))+1)):
      y = int((r**2 - x**2)**(1/2))
      points += (self.line((x + S[0], y + S[1]), (x + S[0], -y + S[1])))
      points += (self.line((y + S[0], x + S[1]), (y + S[0], -x + S[1])))
      points += (self.line((-x + S[0], y + S[1]), (-x + S[0], -y + S[1])))
      points += (self.line((-y + S[0], -x + S[1]), (-y + S[0], x + S[1])))
    return points    

  def triangle(self, A, B, C):  # Come on now, does this need a comment?
    points = []
    points += self.line(A, B)
    points += self.line(A, C)
    points += self.line(B, C)
    return points

  def getY(self, point):
    return point[1]

  def filledTriangle(self, A, B, C):
    points = []
    sortedPoints = sorted([A, B, C], key=self.getY)  # Sorts points based on the Y coordinate
    right = self.line(sortedPoints[0], sortedPoints[2])
    left = self.line(sortedPoints[0], sortedPoints[1]) + self.line(sortedPoints[1], sortedPoints[2])

    xMax = max(A[0], B[0], C[0])
    xMin = min(A[0], B[0], C[0])
    for y in range(self.getY(sortedPoints[0]), self.getY(sortedPoints[2])+1): # This cycle draws lines between the 'left' and the 'right' side of the triangle
      x1 = xMax
      for x in left:
        if(x[1] == y and x[0] < x1):
          x1 = x[0]
      x2 = xMin
      for x in right:
        if(x[1] == y and x[0] > x2):
          x2 = x[0]
      points += self.line((x2, y), (x1, y))
    return points

  def rectangle(self, A, width, height):  # This is a comment
    points = []
    points += self.line(A, (A[0]+width, A[1]))
    points += self.line(A, (A[0], A[1]+height))
    points += self.line((A[0]+width, A[1]), (A[0]+width, A[1]+height))
    points += self.line((A[0], A[1]+height), (A[0]+width, A[1]+height))
    return points

  def filledRectangle(self, A, width, height):  # This is also a comment
    points = []
    points += self.filledTriangle(A, (A[0]+width, A[1]), (A[0], A[1]+height))
    points += self.filledTriangle((A[0]+width, A[1]+height), (A[0]+width, A[1]), (A[0], A[1]+height))
    return points

  def theThiccening(self, inPoints, thiccness): # Oh my god! Look at all this thiccness!
    points = []
    for point in inPoints:
      points += self.filledCircle(point, thiccness/2)
    return points

  def thiccLine(self, A, B, thiccness):
    return self.theThiccening(self.line(A, B), thiccness)

  def thiccTriangle(self, A, B, C, thiccness):
    return self.theThiccening(self.triangle(A, B, C), thiccness)


  def thiccRecrangle(self, A, width, height, thiccness):
    return self.theThiccening(self.rectangle(A, width, height), thiccness)

  def thiccCircle(self, S, r, thiccness):
    return self.theThiccening(self.circle(S, r), thiccness)


  def clear(self, colour):  # Ara ara~~ what a cute little comment
    # for x in range(self.image.width):
    #   for y in range(self.image.height):
    #     self.image.putpixel((x, y), colour)
    self.image = Image.new("RGB", (self.image.width, self.image.height), colour)

  def hex2dec(self, hexIn): # I can't think of another way to say that this comment is redundant
    result = 0
    for index in range(len(hexIn)):
      digit = hexIn[(index+1)*(-1)].upper()
      if(ord("A") <= ord(digit) <= ord("F")):
        digit = ord(digit) - ord('A') + 10
      else:
        digit = int(digit)
      
      result += digit * 16 ** index
    return result

  def hexColour(self, colour):  # As the wild magic sorcerer Blossom would say: "Ooh, pretty colours!"
    colour = colour.replace("#", "")
    r = self.hex2dec(colour[0:2])
    g = self.hex2dec(colour[2:4])
    b = self.hex2dec(colour[4:])
    return (r, g, b)

  def clearWrapper(self, splitLine, scales):
    self.clear(self.hexColour(splitLine[1]))

  def lineWrapper(self, splitLine, scales):
    A = self.convertPoint((float(splitLine[1]), float(splitLine[2])), scales)
    B = self.convertPoint((float(splitLine[3]), float(splitLine[4])), scales)
    thiccness = int(splitLine[5])
    colour = self.hexColour(splitLine[6])
    self.drawPoints(self.thiccLine(A, B, thiccness), colour)

  def rectWrapper(self, splitLine, scales):
    A = self.convertPoint((float(splitLine[1]), float(splitLine[2])), scales)
    width = self.convertSize(float(splitLine[3]), scales)
    height = self.convertSize(float(splitLine[4]), scales)
    thiccness = int(splitLine[5])
    colour = self.hexColour(splitLine[6])
    self.drawPoints(self.thiccRecrangle(A, width, height, thiccness), colour)

  def triangleWrapper(self, splitLine, scales):
    A = self.convertPoint((float(splitLine[1]), float(splitLine[2])), scales)
    B = self.convertPoint((float(splitLine[3]), float(splitLine[4])), scales)
    C = self.convertPoint((float(splitLine[5]), float(splitLine[6])), scales)
    thiccness = self.convertSize(int(splitLine[7]), scales)
    colour = self.hexColour(splitLine[8])
    self.drawPoints(self.thiccTriangle(A, B, C, thiccness), colour)

  def circleWrapper(self, splitLine, scales):
    S = self.convertPoint((float(splitLine[1]), float(splitLine[2])), scales)
    r = self.convertSize(float(splitLine[3]), scales)
    thiccness = int(splitLine[4])
    colour = self.hexColour(splitLine[5])
    self.drawPoints(self.thiccCircle(S, r, thiccness), colour)

  def fillCircleWrapper(self, splitLine, scales):
    S = self.convertPoint((float(splitLine[1]), float(splitLine[2])), scales)
    r = self.convertSize(float(splitLine[3]), scales)
    colour = self.hexColour(splitLine[4])
    self.drawPoints(self.filledCircle(S, r), colour)

  def fillTriangleWrapper(self, splitLine, scales):
    A = self.convertPoint((float(splitLine[1]), float(splitLine[2])), scales)
    B = self.convertPoint((float(splitLine[3]), float(splitLine[4])), scales)
    C = self.convertPoint((float(splitLine[5]), float(splitLine[6])), scales)
    colour = self.hexColour(splitLine[7])
    self.drawPoints(self.filledTriangle(A, B, C), colour)

  def fillRectWrapper(self, splitLine, scales):
    A = self.convertPoint((float(splitLine[1]), float(splitLine[2])), scales)
    width = self.convertSize(float(splitLine[3]), scales)
    height = self.convertSize(float(splitLine[4]), scales)
    colour = self.hexColour(splitLine[5])
    self.drawPoints(self.filledRectangle(A, width, height), colour)

  def vesWrapper(self, splitLine, scales):
    print("Version " + str(splitLine[1]) + "\n" + "File width " + str(splitLine[2]) + "\n" + "File height " + str(splitLine[3]))

  def grayscale(self, splitline, scales):
    for x in range(self.image.width):
      for y in range(self.image.height):
        colour = self.image.getpixel((x, y))
        grayscaled = int((colour[0] + colour[1] + colour[2])/3) 
        colour = (grayscaled, grayscaled, grayscaled)
        self.image.putpixel((x, y), colour)

  def interpret(self, scales, path = None):  # This finction goes through all lines in file 'path' and looks for valid VES commands
    commands = ["CLEAR", "LINE", "RECT", "TRIANGLE", "CIRCLE", 
                "FILL_CIRCLE", "FILL_TRIANGLE", "FILL_RECT", "VES", 
                "GRAYSCALE"]
    functions = [self.clearWrapper, self.lineWrapper, 
                 self.rectWrapper, self.triangleWrapper, 
                 self.circleWrapper, self.fillCircleWrapper, 
                 self.fillTriangleWrapper, self.fillRectWrapper, 
                 self.vesWrapper, self.grayscale]
    if(path != None):
      with open(path) as file:
        onLine = 0
        for line in file:
          onLine += 1
          splitLine = line.split()
          try:
            functions[commands.index(splitLine[0])](splitLine, scales)
          except ValueError:
            print("Syntax error on line "+str(onLine)+": Unknown command "+splitLine[0])
    else:
      onLine = 0
      for vesObj in self.objects:
        onLine += 1
        try:
          functions[commands.index(vesObj.command)]([vesObj.command]+vesObj.attributes, scales)
        except ValueError:
          print("Syntax error on line "+str(onLine)+": Unknown command "+splitLine[0])
    
  def addObject(self, command, attributes, silent = 0):
    commands = ["CLEAR", "LINE", "RECT", "TRIANGLE", "CIRCLE", "FILL_CIRCLE", "FILL_TRIANGLE", "FILL_RECT", "VES", "GRAYSCALE"]
    attributeNum = [1, 6, 6, 8, 5, 4, 7, 5, 3, 0]
    if(command.upper() in commands):
      if(attributeNum[commands.index(command)] == len(attributes)):
        self.objects.append(self.vesObject(command.upper(), attributes))
        if(not silent):
          print("Object " + command.upper() + " with attributes " + str(attributes) + " added.")
      else:
        print("Incorrect number of attributes, command " + command.upper() + " requires " + attributeNum[commands.index(command)] + " attributes, " + len(attributes) + " were given.")
    else:
      print("Incorrect command '"+command+"' .")
  
  def makeFile(self, path):
    with open(path, 'w') as file:
      for obj in self.objects:
        line = obj.command
        for attribute in obj.attributes:
          line += " "+str(attribute)
        line += "\n"
        file.write(line)
    return (path)

  def show(self, scale = 1):
    width = int(self.defWidth * scale)
    height = int(self.defHeight * scale)
    # path = str(time())
    # self.makeFile(path)
    self.image = Image.new("RGB", (width, height), (255, 255, 255))
    self.interpret([self.defWidth, self.defHeight, width, height], path = None)
    display(self.image)
    # remove(path)
  # def gib(self):
  #   return outImage
  
  def fromStr(self, vesStr):
    for line in vesStr.split("\n"):
      # if("VES" in line):
      #   self = __init__()
      splitLine = line.split(" ")
      attr = splitLine[1:]
      # print(splitLine, attr)
      # if(attr == None):
      #   attr = []
      # input()
      self.addObject(splitLine[0].upper(), attr, silent=1)
    
  def fromFile(self, file):
    raise NotImplementedError # Toto dokonci
    
  def getImage(self, scale = 1):
    width = int(self.defWidth * scale)
    height = int(self.defHeight * scale)
    self.image = Image.new("RGB", (width, height), (255, 255, 255))
    self.interpret([self.defWidth, self.defHeight, width, height], path = None)
    imgInMem = BytesIO()
    self.image.save(imgInMem, 'PNG', quality=70)
    imgInMem.seek(0)
    return imgInMem


  def __init__(self, initial=None, vesStr=None, file=None):
    self.objects = []
    self.image = None
    self.faster = 1
    if(initial != None):
      self.addObject('VES', initial)
    elif(vesStr != None):
      self.fromStr(vesStr)
    elif(file != None): 
      self.fromFile(file)
    self.defWidth = int(self.objects[0].attributes[1])
    self.defHeight = int(self.objects[0].attributes[2])

if(__name__ == "__main__"): #Demo/test
  defWidth = 80
  defHeight = 120
  bgColour = "#A44A3D"
  objColour = "#F29E8E"
  vesStr = f"""VES 1.0 {defWidth} {defHeight}
CLEAR {bgColour}
FILL_CIRCLE 40 42 25 {objColour}
FILL_CIRCLE 40 47 22 {bgColour}
TRIANGLE 40 47 15 85 65 85 2 {objColour}
TRIANGLE 40 47 26 68 54 68 2 {objColour}
FILL_TRIANGLE 25 24 25 29 29 26.4 {bgColour}
FILL_TRIANGLE 55 24 55 29 51 26.4 {bgColour}
FILL_TRIANGLE 40 20 38 24 42 24 {bgColour}"""
  
  vesObj = ves(vesStr=vesStr)
  
  imgInMem = vesObj.getImage(scale = 4)
  with open("string.png", 'wb') as file:
    file.write(imgInMem.getbuffer())