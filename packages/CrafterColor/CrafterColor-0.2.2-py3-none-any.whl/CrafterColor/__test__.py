from CrafterColor.Print import * #import Everything and import print func
from CrafterColor import * #import Everything
activeColor() #trun on the Colors
print("normal COLOR",color="normal") # 'normal' means no colors
normal = "normal"
for LOF in printColors:
	print("Hello, World",LOF,sep=": ",bg=None,color=LOF)
print("random Color:",repr(Color(type='random')),color=normal)
# dum="_" make random colors from the <Colors class> =:= Colors.random() ; default Color(type="random")
array = ColorArray(range(0,10),dum="_")
for color in array:
	print(repr(color))
	#print((color.__dict__),color=None),bg=Colors.random().color
