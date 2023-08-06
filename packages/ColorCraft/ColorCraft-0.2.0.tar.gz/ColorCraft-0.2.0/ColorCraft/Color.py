from .Errors import *
import random
import os
def colorize(text, color):
	r,g,b = Colors.hex2rgb(color)
	return f"\033[38;2;{r};{g};{b}m{text}\033[0m"

class ColorObj(object):
	"""a basic ColorObject"""
	def __init__(self, color,name=None):
		super(ColorObj, self).__init__()
		self.color = color
		self.name = name
	def __repr__(self):
		name = (",name="+repr(self.name) if self.name is not None else "")
		return f"<ColorObject(color={self.color}{name})>"
class Colors(object):
	""" Colors class """
	def random():
		""" random function return ColorObj; a random color from the Colors.rgb class """
		ran = None
		while not isinstance(ran,tuple):
			item = random.choice(list(Colors.rgb.__dict__.items()))
			ran = item[1]
			name = item[0]
		return ColorObj(color=ran,name=name)
	def random_rgb():
		return tuple([random.randint(0,255) for _ in range(3)])
	def rgb2hex(rgb):
		""" reTRUN RGB TO HEX """
		return '%02x%02x%02x' % rgb
	def hex2rgb(color):
		""" reTRUN HEX TO RGB """
		h = color.lstrip('#') if "#" in color else color
		rgb = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
		return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
	def int2hex(int):
		""" reTRUN INT TO HEX : hex(x) """
		return hex(int)
	def hex2int(hex):
		""" reTRUN HEX TO INT : hex(x) """
		return int(hex,16)
	def hsl2rgb(h,s,l):
		""" reTRUN HSL TO RGB """
		a = s*min(l,1-l)
		n = (a-min(h,s,l))
		def f(n,k=(n+h/30)%12): return l - a*max(min(k-3,9-k,1),-1)
		return [f(0),f(8),f(4)]
	class rgb:
		""" rgb class Contain colors """
		yellow      = (255,255,0)
		gold        = (255,215,0)
		red         = (255,0,0)
		orange      = (255,165,0)
		lime        = (0,255,0)
		green       = (0,128+20,0)
		darkgreen   = (0,100,0)
		teal        = (0,128,128)
		cyan        = (0,255,255)
		deepskyblue = (0,191,255)
		skyblue     = (135,206,235)
		blue        = (0,0,255)
		violet      = (138,43,226)
		purple      = (128,0,128)
		testypurple = (175, 15, 175)
		hotpink     = (255,105,180)
		deeppink    = (255,20,147)
		pink        = (255,192,203)
		brown       = (139,69,19)
		black       = (0,0,0)
		white       = (255,255,255)
		gray        = (105,105,105)
		drakgray    = (128,128,128)
		silver      = (192,192,192)
	class terminalColors:
		""" Terminal Colors class Contain 'OKGREEN','WARNING','HEADER',etc and ENDC,BOLD,UNDERLINE """
		HEADER = 'B4009E'
		OKBLUE = '3B78FF'
		OKCYAN = '61D6D6'
		OKGREEN = '16C60C'
		WARNING = 'FFED48'
		FAIL = 'F03C4B'
		ENDC = '\033[0m'
		BOLD = '\033[1m'
		UNDERLINE = '\033[4m'
def activeColor():
	""" make printing color possible, no idea how but thanks to https://stackoverflow.com/a/54955094/19313724 """
	os.system("")
class Color(object):
	"""
	Color object
	Color(color=None,*,name=None,type="hex",show=True)
		color: the color \\% there is three types = ["rgb","hex","random"]
		name : the color name; to name the obj
		type : the color type
		show : on repr show color or not
	"""
	def __init__(self, color=None,*,name=None,type="hex",show=True):
		super(Color, self).__init__()
		self.color = color
		self.type  = type
		self.show  = show
		self.name  = name
		types = ["rgb","hex","random"]
		if type.lower() not in types:
			raise TypeError(f"type is not defined {color}:{type}")
		elif color is None and type!="random":
			raise ValueError(f"expected type {type} but get {color}")
		else:
			if   type.lower() == 'rgb':
				self.Hexcolor = Colors.rgb2hex(color)
				self.Intcolor = Colors.hex2int(self.Hexcolor)
			elif type.lower() == 'hex':
				self.Intcolor = Colors.hex2int(color)
				self.Hexcolor = color
			elif type.lower() == 'random':
				color = Colors.random_rgb()
				self.color = color
				self.type  = 'rgb'
				self.Hexcolor = Colors.rgb2hex(color)
				self.Intcolor = Colors.hex2int(self.Hexcolor)
		if self.Intcolor not in range(16777216):
			raise UnownColor(f"Unown Color {color}")
		self.Exception = None
	def colorize(self,text="█"):
		""" return a color text """
		return colorize(text,"#"+self.Hexcolor)
	def print(self,text="█"):
		""" print a color text """
		return print(self.colorize(text))
	def __bool__(self):
		""" return bool """
		return self.Intcolor != 0
	def __int__(self):
		""" return color number """
		return self.Intcolor
	def __hex__(self):
		""" return hex color """
		return int(self)
	def __str__(self):
		""" return str = "#"+hex """
		return "#"+self.Hexcolor
	def __format__(self,formated):
		""" Color object format """
		been_change = 0
		if self.show and not self.Exception:
			self.show = False
			been_change = 1
			farme = format(repr(self),formated)
		else:
			exceptions = [repr(self).split("<")[0]]+(repr(self).split("<"))[1].split(">")
			farme = exceptions[0]+format(exceptions[1],formated)+exceptions[2]
		if not self.show and been_change:
			self.show = True
		return farme
	def __repr__(self):
		""" repr return Color repr with the color """
		name = (",name="+repr(self.name) if self.name is not None else "")
		ColorRepr = f"<Color(color={self.Intcolor},hex={repr(self.Hexcolor)}{name})>"
		try:
			if self.show: return colorize(ColorRepr,"#"+self.Hexcolor)
			else: return ColorRepr
		except Exception as e:
			return ColorRepr

class ColorArray(object):
	"""docstring for ColorArray"""
	def __init__(self, colors=[],dum="random"):
		super(ColorArray, self).__init__()
		self.colors = []
		if isinstance(colors,range):
			if dum == "random":
				for _ in colors:
					self.append(Color(None,type="random"))
			elif dum.startswith("blank::"):
				try:
					name = dum.split("::")[1]
					color = Colors.rgb.__dict__[name]
				except KeyError:
					raise ColorError(f"color rgb does not exist in Colors.rgb : {repr(name)}")
				except IndexError:
					raise UnownColor(f"exacpted color name but get nothing")
				for _ in colors:
					self.append(Color(color,name=name,type="rgb"))
			else:
				for _ in colors:
					obj = Colors.random()
					self.append(Color(obj.color,name=obj.name,type="rgb"))
		else:
			for color in colors:
				self.append(color)
		self.index_ = 0
		self.POP   = None
	def copy(self):
		return self.__list__()
	def __len__(self):
		""" colors list len """
		return len(self.colors)
	def __bool__(self):
		""" colors bool """
		return bool(self.colors)
	def __list__(self):
		""" copy of ColorArray """
		return ColorArray(self.colors.copy())
	def __add__(self,other):
		""" add list of colors or ColorArray object """
		if   isinstance(other,(dict,list,tuple,set,str)): other
		elif isinstance(other,ColorArray): other = other.colors
		else: raise TypeError("unsupported operand type(s) for +: '{type}' and '{other}'"\
			.format(other=other.__class__.__name__,type=self.__class__.__name__))
		return ColorArray(self.colors+list(other))
	def __getitem__(self,index_):
		""" get an item by index_ """
		return self.colors[index_]
	def __del__(self):
		""" del an item """
		del (self)
	def __iter__(self):
		return iter(self.colors)
	def __reset__(self):
		self.index_ = 0
		self.POP   = None if not bool(self.colors) else self.colors[self.index_]
	def __next__(self):
		if self.index_ <= len(self.colors)-1:
			self.__reset__()
			raise StopIteration
		else:
			self.POP   = self.colors[self.index_]
			self.index_+=1
		return self.POP
	def append(self,color):
		""" append a new Color """
		if isinstance(color,str):
			self.colors.append(Color(color,type="hex"))
		elif isinstance(color,Color):
			self.colors.append(color)
		else:
			if color is not None:raise UnownColor(f"Unown Color {color}:{color.__class__.__name__}")
	def remove(self,color):
		try:
			return self.colors.remove(color)
		except ValueError as e:
			pass
		raise ValueError(f"ColorArray.remove(color): {repr(color)} not in ColorArray")
	def pop(self,index_):
		return self.colors.pop(index_)
	def index(self,color):
		try:
			return self.colors.index(color)
		except ValueError as e:
			pass
		raise ValueError(f"ColorArray.index(color): {repr(color)} not in ColorArray")
	def isin(self,item):
		return int(item in self.colors)
	def count(self,item):
		return self.colors.count(item)
	def clear(self):
		return self.colors.clear()
	def reverse(self):
		return self.colors.reverse()
	def insert(self,index, object):
		return self.colors.insert()
	def sort(self,*args,**kw):
		return self.colors.sort(*args,**kw)
	def extend(self,iterable):
		return self.colors.extend(iterable)
	def getattr(self,*args,**kw):
		return getattr(self.colors,*args,**kw)
	def display_(self,colorize=False,text="",Exception=False):
		farme =  ""
		farme += ("{:<50}| {:<}".format("Color Object", "Color"))+"\n"
		farme += ("-"*60)+"\n"
		for c in self.colors:
			c.Exception = True if Exception else False
			farme += ("{:<50}| {:<}".format(c, c.colorize() if not colorize else c.colorize(text)))+"\n"
			c.Exception = False if Exception else None
		return farme

	def display(self,colorize=False,text="",Exception=False):
		print("{:<50}| {:<}".format("Color Object", "Color"))
		print("-"*60)
		for c in self.colors:
			c.Exception = True if Exception else False
			print(("{:<50}| {:<}".format(c, c.colorize() if not colorize else c.colorize(text))))
			c.Exception = False if Exception else None
	def __repr__(self):
		return f"<Array({self.colors})>"