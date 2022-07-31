"""
Pencil Sketchify Action Module
"""
from time import perf_counter
import photoshop.api as ps
app = ps.Application()
cID = app.charIDToTypeID
sID = app.stringIDToTypeID
dialog_mode = ps.DialogModes.DisplayNoDialogs


"""
HELPERS
"""


def new_layer(id):
	desc1 = ps.ActionDescriptor()
	ref1 = ps.ActionReference()
	ref1.putClass(cID('Lyr '))
	desc1.putReference(cID('null'), ref1)
	desc1.putInteger(cID('LyrI'), id)
	app.executeAction(cID('Mk  '), desc1, dialog_mode)


def select_bg():
	desc1 = ps.ActionDescriptor()
	ref1 = ps.ActionReference()
	ref1.putName(cID('Lyr '), "Background")
	desc1.putReference(cID('null'), ref1)
	desc1.putBoolean(cID('MkVs'), False)
	list1 = ps.ActionList()
	list1.putInteger(1)
	desc1.putList(cID('LyrI'), list1)
	app.executeAction(cID('slct'), desc1, dialog_mode)


def reset_colors():
	"""
	desc1 = ps.ActionDescriptor()
	ref1 = ps.ActionReference()
	ref1.putProperty(cID('Clr '), cID('Clrs'))
	desc1.putReference(cID('null'), ref1)
	app.executeAction(cID('Rset'), desc1, dialog_mode)
	"""
	pass


def move_layer(pos, id):
	if isinstance(id, int): id = [id]
	desc1 = ps.ActionDescriptor()
	ref1 = ps.ActionReference()
	ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
	desc1.putReference(cID('null'), ref1)
	ref2 = ps.ActionReference()
	ref2.putIndex(cID('Lyr '), pos)
	desc1.putReference(cID('T   '), ref2)
	desc1.putBoolean(cID('Adjs'), False)
	desc1.putInteger(cID('Vrsn'), 5)
	list1 = ps.ActionList()
	for i in id:
		list1.putInteger(i)
	desc1.putList(cID('LyrI'), list1)
	app.executeAction(cID('move'), desc1, dialog_mode)


def set_opacity(opacity):
	desc1 = ps.ActionDescriptor()
	ref1 = ps.ActionReference()
	ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
	desc1.putReference(cID('null'), ref1)
	desc2 = ps.ActionDescriptor()
	desc2.putUnitDouble(cID('Opct'), cID('#Prc'), opacity)
	desc1.putObject(cID('T   '), cID('Lyr '), desc2)
	app.executeAction(cID('setd'), desc1, dialog_mode)


def select_layer(name, id):
	desc1 = ps.ActionDescriptor()
	ref1 = ps.ActionReference()
	ref1.putName(cID('Lyr '), name)
	desc1.putReference(cID('null'), ref1)
	desc1.putBoolean(cID('MkVs'), False)
	list1 = ps.ActionList()
	list1.putInteger(id)
	desc1.putList(cID('LyrI'), list1)
	app.executeAction(cID('slct'), desc1, dialog_mode)


def select_layers(name, layers):
	desc1 = ps.ActionDescriptor()
	ref1 = ps.ActionReference()
	ref1.putName(cID('Lyr '), name)
	desc1.putReference(cID('null'), ref1)
	desc1.putEnumerated(
		sID("selectionModifier"), sID("selectionModifierType"), sID("addToSelection"))
	desc1.putBoolean(cID('MkVs'), False)
	list1 = ps.ActionList()
	for layer in layers:
		list1.putInteger(layer)
	desc1.putList(cID('LyrI'), list1)
	app.executeAction(cID('slct'), desc1, dialog_mode)


def auto_tone():
	desc1 = ps.ActionDescriptor()
	desc1.putBoolean(cID('Auto'), True)
	app.executeAction(cID('Lvls'), desc1, dialog_mode)


def auto_contrast():
	desc1 = ps.ActionDescriptor()
	desc1.putBoolean(cID('AuCo'), True)
	app.executeAction(cID('Lvls'), desc1, dialog_mode)


def hide_layer(name=None):
	desc1 = ps.ActionDescriptor()
	list1 = ps.ActionList()
	ref1 = ps.ActionReference()
	if name: ref1.putName(cID('Lyr '), name)
	else: ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
	list1.putReference(ref1)
	desc1.putList(cID('null'), list1)
	app.executeAction(cID('Hd  '), desc1, dialog_mode)


def show_layer(name=None):
	desc1 = ps.ActionDescriptor()
	list1 = ps.ActionList()
	ref1 = ps.ActionReference()
	if name: ref1.putName(cID('Lyr '), name)
	else: ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
	list1.putReference(ref1)
	desc1.putList(cID('null'), list1)
	app.executeAction(cID('Shw '), desc1, dialog_mode)


def delete_layers(layers):
	desc1 = ps.ActionDescriptor()
	ref1 = ps.ActionReference()
	ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
	desc1.putReference(cID('null'), ref1)
	list1 = ps.ActionList()
	for layer in layers:
		list1.putInteger(layer)
	desc1.putList(cID('LyrI'), list1)
	app.executeAction(cID('Dlt '), desc1, dialog_mode)


"""
BLENDING MODES
"""


def blend(key):
	desc1 = ps.ActionDescriptor()
	ref1 = ps.ActionReference()
	ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
	desc1.putReference(cID('null'), ref1)
	desc2 = ps.ActionDescriptor()
	desc2.putEnumerated(cID('Md  '), cID('BlnM'), sID(key))
	desc1.putObject(cID('T   '), cID('Lyr '), desc2)
	app.executeAction(cID('setd'), desc1, dialog_mode)


# Utility commands
def blend_multiply(): blend('multiply')
def blend_color_dodge(): blend('colorDodge')
def blend_linear_light(): blend("linearLight")
def blend_linear_burn(): blend("linearBurn")
def blend_soft_light(): blend('softLight')
def blend_screen(): blend('screen')
def blend_overlay(): blend('overlay')
def blend_color(): blend('color')


def run(draft_sketch=False, rough_sketch=False, colored=True):
	"""
	Pencil Sketchify Steps
	"""

	# Is the main layer "Layer 1"
	app.activeDocument.activeLayer.name = "Background"

	# Make - New Layer 1
	new_layer(139)

	# Select
	select_bg()

	# Make - Solid Color Layer
	desc1 = ps.ActionDescriptor()
	ref1 = ps.ActionReference()
	ref1.putClass(sID("contentLayer"))
	desc1.putReference(cID('null'), ref1)
	desc2 = ps.ActionDescriptor()
	desc3 = ps.ActionDescriptor()
	desc4 = ps.ActionDescriptor()
	desc4.putInteger(cID('Rd  '), 166)
	desc4.putInteger(cID('Grn '), 166)
	desc4.putInteger(cID('Bl  '), 166)
	desc3.putObject(cID('Clr '), sID("RGBColor"), desc4)
	desc2.putObject(cID('Type'), sID("solidColorLayer"), desc3)
	desc1.putObject(cID('Usng'), sID("contentLayer"), desc2)
	app.executeAction(cID('Mk  '), desc1, dialog_mode)

	# Select
	select_bg()

	# Layer Via Copy - Background copy
	app.executeAction(sID('copyToLayer'), ps.ActionDescriptor(), dialog_mode)

	# Move
	move_layer(3, 240)

	# Reset Colors
	reset_colors()

	# Filter Gallery - Photocopy
	desc1 = ps.ActionDescriptor()
	desc1.putEnumerated(cID('GEfk'), cID('GEft'), cID('Phtc'))
	desc1.putInteger(cID('Dtl '), 2)
	desc1.putInteger(cID('Drkn'), 5)
	app.executeAction(1195730531, desc1, dialog_mode)

	# Set - Blending Multiply
	blend_multiply()

	# Select
	select_bg()

	# Layer Via Copy - Background copy 2
	app.executeAction(sID('copyToLayer'), ps.ActionDescriptor(), dialog_mode)

	# Move
	move_layer(4, 242)

	# Reset Colors
	reset_colors()

	# Filter Gallery - Photocopy, Accented Edges
	desc1 = ps.ActionDescriptor()
	list1 = ps.ActionList()
	desc2 = ps.ActionDescriptor()
	desc2.putEnumerated(cID('GEfk'), cID('GEft'), cID('AccE'))
	desc2.putInteger(cID('EdgW'), 3)
	desc2.putInteger(cID('EdgB'), 20)
	desc2.putInteger(cID('Smth'), 15)
	list1.putObject(cID('GEfc'), desc2)
	desc3 = ps.ActionDescriptor()
	desc3.putEnumerated(cID('GEfk'), cID('GEft'), cID('Phtc'))
	desc3.putInteger(cID('Dtl '), 1)
	desc3.putInteger(cID('Drkn'), 49)
	list1.putObject(cID('GEfc'), desc3)
	desc1.putList(cID('GEfs'), list1)
	app.executeAction(1195730531, desc1, dialog_mode)

	# Set - Blending Multiply
	blend_multiply()

	# Select
	select_bg()

	# Layer Via Copy - Background Copy 3
	app.executeAction(sID('copyToLayer'), ps.ActionDescriptor(), dialog_mode)

	# Move
	move_layer(5, 244)

	# Reset Colors
	reset_colors()

	# Filter Gallery - Photocopy, Stamp
	desc1 = ps.ActionDescriptor()
	list1 = ps.ActionList()
	desc2 = ps.ActionDescriptor()
	desc2.putEnumerated(cID('GEfk'), cID('GEft'), cID('Stmp'))
	desc2.putInteger(cID('LgDr'), 25)
	desc2.putInteger(cID('Smth'), 40)
	list1.putObject(cID('GEfc'), desc2)
	desc3 = ps.ActionDescriptor()
	desc3.putEnumerated(cID('GEfk'), cID('GEft'), cID('Phtc'))
	desc3.putInteger(cID('Dtl '), 1)
	desc3.putInteger(cID('Drkn'), 49)
	list1.putObject(cID('GEfc'), desc3)
	desc1.putList(cID('GEfs'), list1)
	app.executeAction(1195730531, desc1, dialog_mode)

	# Set - Blending Multiply
	blend_multiply()

	# Set
	set_opacity(25)

	# Select
	select_bg()

	# Layer Via Copy - Background Copy 4
	app.executeAction(sID('copyToLayer'), ps.ActionDescriptor(), dialog_mode)

	# Move
	move_layer(6, 246)

	# Reset
	reset_colors()

	# Filter Gallery - Glowing Edge
	desc1 = ps.ActionDescriptor()
	desc1.putEnumerated(cID('GEfk'), cID('GEft'), cID('GlwE'))
	desc1.putInteger(cID('EdgW'), 1)
	desc1.putInteger(cID('EdgB'), 20)
	desc1.putInteger(cID('Smth'), 15)
	app.executeAction(1195730531, desc1, dialog_mode)

	# Desaturate
	app.executeAction(cID('Dstt'), ps.ActionDescriptor(), dialog_mode)

	# Levels - Auto Tone
	auto_tone()

	# Levels - Auto Contrast
	auto_contrast()

	# Levels Adjustment
	desc1 = ps.ActionDescriptor()
	desc1.putEnumerated(sID("presetKind"), sID("presetKindType"), sID("presetKindCustom"))
	list1 = ps.ActionList()
	desc2 = ps.ActionDescriptor()
	ref1 = ps.ActionReference()
	ref1.putEnumerated(cID('Chnl'), cID('Chnl'), cID('Cmps'))
	desc2.putReference(cID('Chnl'), ref1)
	list2 = ps.ActionList()
	list2.putInteger(25)
	list2.putInteger(230)
	desc2.putList(cID('Inpt'), list2)
	list1.putObject(cID('LvlA'), desc2)
	desc1.putList(cID('Adjs'), list1)
	app.executeAction(cID('Lvls'), desc1, dialog_mode)

	# Invert
	app.executeAction(cID('Invr'), ps.ActionDescriptor(), dialog_mode)

	# Set
	blend_multiply()

	# Select
	select_bg()

	# Layer Via Copy - Background Copy 5
	app.executeAction(sID('copyToLayer'), ps.ActionDescriptor(), dialog_mode)

	# Move
	move_layer(7, 248)

	# Layer Via Copy - Background Copy 6
	app.executeAction(sID('copyToLayer'), ps.ActionDescriptor(), dialog_mode)

	# Invert
	app.executeAction(cID('Invr'), ps.ActionDescriptor(), dialog_mode)

	# Gaussian Blur
	desc1 = ps.ActionDescriptor()
	desc1.putUnitDouble(cID('Rds '), cID('#Pxl'), 50)
	app.executeAction(sID('gaussianBlur'), desc1, dialog_mode)

	# Set - Blending Color Dodge
	blend_color_dodge()

	# Select
	select_layers("Background copy 5", [248, 249])

	# Merge Layers
	app.executeAction(sID('mergeLayersNew'), ps.ActionDescriptor(), dialog_mode)

	# Desaturate
	app.executeAction(cID('Dstt'), ps.ActionDescriptor(), dialog_mode)

	# Layer Via Copy - Background Copy 7
	app.executeAction(sID('copyToLayer'), ps.ActionDescriptor(), dialog_mode)

	# Reset
	reset_colors()

	# Filter Gallery - Glowing Edge
	desc1 = ps.ActionDescriptor()
	desc1.putEnumerated(cID('GEfk'), cID('GEft'), cID('GlwE'))
	desc1.putInteger(cID('EdgW'), 1)
	desc1.putInteger(cID('EdgB'), 20)
	desc1.putInteger(cID('Smth'), 15)
	app.executeAction(1195730531, desc1, dialog_mode)

	# Invert
	app.executeAction(cID('Invr'), ps.ActionDescriptor(), dialog_mode)

	# Set
	blend_multiply()

	# Set
	set_opacity(80)

	# Select
	select_layers("Background copy 6", [249, 250])

	# Merge Layers
	app.executeAction(sID('mergeLayersNew'), ps.ActionDescriptor(), dialog_mode)

	# Select
	select_bg()

	# Layer Via Copy - Background Copy 5
	app.executeAction(sID('copyToLayer'), ps.ActionDescriptor(), dialog_mode)

	# Move
	move_layer(8, 252)

	# Desaturate
	app.executeAction(cID('Dstt'), ps.ActionDescriptor(), dialog_mode)

	# High Pass Filter
	desc1 = ps.ActionDescriptor()
	desc1.putUnitDouble(cID('Rds '), cID('#Pxl'), 30)
	app.executeAction(sID('highPass'), desc1, dialog_mode)

	# Set - Blending Linear Light
	blend_linear_light()

	# Set - Layer Style, Blending Options: Blend if Gray
	desc1 = ps.ActionDescriptor()
	ref1 = ps.ActionReference()
	ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
	desc1.putReference(cID('null'), ref1)
	desc2 = ps.ActionDescriptor()
	list1 = ps.ActionList()
	desc3 = ps.ActionDescriptor()
	ref2 = ps.ActionReference()
	ref2.putEnumerated(cID('Chnl'), cID('Chnl'), cID('Gry '))
	desc3.putReference(cID('Chnl'), ref2)
	desc3.putInteger(cID('SrcB'), 0)
	desc3.putInteger(cID('Srcl'), 0)
	desc3.putInteger(cID('SrcW'), 75)
	desc3.putInteger(cID('Srcm'), 125)
	desc3.putInteger(cID('DstB'), 55)
	desc3.putInteger(cID('Dstl'), 125)
	desc3.putInteger(cID('DstW'), 255)
	desc3.putInteger(cID('Dstt'), 255)
	list1.putObject(cID('Blnd'), desc3)
	desc2.putList(cID('Blnd'), list1)
	desc1.putObject(cID('T   '), cID('Lyr '), desc2)
	app.executeAction(cID('setd'), desc1, dialog_mode)

	# Set
	set_opacity(50)

	# Select
	select_bg()

	# Layer Via Copy - Background Copy 6
	app.executeAction(sID('copyToLayer'), ps.ActionDescriptor(), dialog_mode)

	# Move
	move_layer(9, 254)

	# Reset
	reset_colors()

	# Filter Gallery - Cutout
	desc1 = ps.ActionDescriptor()
	desc1.putEnumerated(cID('GEfk'), cID('GEft'), cID('Ct  '))
	desc1.putInteger(cID('NmbL'), 8)
	desc1.putInteger(cID('EdgS'), 10)
	desc1.putInteger(cID('EdgF'), 1)
	app.executeAction(1195730531, desc1, dialog_mode)

	# Desaturate
	app.executeAction(cID('Dstt'), ps.ActionDescriptor(), dialog_mode)

	# Levels - Auto Tone
	auto_tone()

	# Levels - Auto Contrast
	auto_contrast()

	# Color Range
	desc1 = ps.ActionDescriptor()
	desc1.putEnumerated(cID('Clrs'), cID('Clrs'), cID('Mdtn'))
	desc1.putInteger(sID("midtonesFuzziness"), 40)
	desc1.putInteger(sID("midtonesLowerLimit"), 105)
	desc1.putInteger(sID("midtonesUpperLimit"), 150)
	desc1.putInteger(sID("colorModel"), 0)
	app.executeAction(sID('colorRange'), desc1, dialog_mode)

	# Layer Via Copy - Layer 2
	app.executeAction(sID('copyToLayer'), ps.ActionDescriptor(), dialog_mode)

	# Find Edges
	app.executeAction(sID('findEdges'), ps.ActionDescriptor(), dialog_mode)

	# Hide
	hide_layer("Background copy 6")

	# Hide
	hide_layer()

	# Select
	select_bg()

	# Layer Via Copy - Background copy 8
	app.executeAction(sID('copyToLayer'), ps.ActionDescriptor(), dialog_mode)

	# Move
	move_layer(9, 257)

	# Reset
	reset_colors()

	# Filter Gallery - Cutout
	desc1 = ps.ActionDescriptor()
	desc1.putEnumerated(cID('GEfk'), cID('GEft'), cID('Ct  '))
	desc1.putInteger(cID('NmbL'), 8)
	desc1.putInteger(cID('EdgS'), 8)
	desc1.putInteger(cID('EdgF'), 1)
	app.executeAction(1195730531, desc1, dialog_mode)

	# Desaturate
	app.executeAction(cID('Dstt'), ps.ActionDescriptor(), dialog_mode)

	# Levels
	auto_tone()

	# Levels
	auto_contrast()

	# Color Range
	desc1 = ps.ActionDescriptor()
	desc1.putEnumerated(cID('Clrs'), cID('Clrs'), cID('Mdtn'))
	desc1.putInteger(sID("midtonesFuzziness"), 40)
	desc1.putInteger(sID("midtonesLowerLimit"), 105)
	desc1.putInteger(sID("midtonesUpperLimit"), 150)
	desc1.putInteger(sID("colorModel"), 0)
	app.executeAction(sID('colorRange'), desc1, dialog_mode)

	# Layer Via Copy - Layer 3
	app.executeAction(sID('copyToLayer'), ps.ActionDescriptor(), dialog_mode)

	# Find Edges
	app.executeAction(sID('findEdges'), ps.ActionDescriptor(), dialog_mode)

	# Select
	select_layer("Background copy 8", 257)

	# Select
	select_layers("Background copy 6", [257, 254])

	# Delete
	delete_layers([257, 254])

	# Select
	select_layer("Layer 2", 255)

	# Show
	show_layer()

	# Select
	select_layers("Layer 3", [258, 255])

	# Set
	blend_multiply()

	# Set
	set_opacity(30)

	# Select
	select_layer("Background copy 3", 244)

	# Set
	set_opacity(30)

	# Select
	select_layer("Background copy 7", 250)

	# Move
	move_layer(2, 250)

	# Select
	select_layer("Background copy 5", 252)

	# Move
	move_layer(10, 252)

	# Select
	select_layer("Background copy 7", 250)

	# Set
	set_opacity(50)

	# Select
	select_bg()

	# Layer Via Copy - Background Copy 6
	app.executeAction(sID('copyToLayer'), ps.ActionDescriptor(), dialog_mode)

	# Move
	move_layer(11, 261)

	# Filter - Distort Wave
	desc1 = ps.ActionDescriptor()
	desc1.putEnumerated(cID('Wvtp'), cID('Wvtp'), cID('WvSn'))
	desc1.putInteger(cID('NmbG'), 5)
	desc1.putInteger(cID('WLMn'), 10)
	desc1.putInteger(cID('WLMx'), 500)
	desc1.putInteger(cID('AmMn'), 5)
	desc1.putInteger(cID('AmMx'), 35)
	desc1.putInteger(cID('SclH'), 100)
	desc1.putInteger(cID('SclV'), 100)
	desc1.putEnumerated(cID('UndA'), cID('UndA'), cID('RptE'))
	desc1.putInteger(cID('RndS'), 1260853)
	app.executeAction(cID('Wave'), desc1, dialog_mode)

	# Reset
	reset_colors()

	# Filter Gallery - Photocopy, Accented Edges
	desc1 = ps.ActionDescriptor()
	list1 = ps.ActionList()
	desc2 = ps.ActionDescriptor()
	desc2.putEnumerated(cID('GEfk'), cID('GEft'), cID('AccE'))
	desc2.putInteger(cID('EdgW'), 3)
	desc2.putInteger(cID('EdgB'), 20)
	desc2.putInteger(cID('Smth'), 15)
	list1.putObject(cID('GEfc'), desc2)
	desc3 = ps.ActionDescriptor()
	desc3.putEnumerated(cID('GEfk'), cID('GEft'), cID('Phtc'))
	desc3.putInteger(cID('Dtl '), 1)
	desc3.putInteger(cID('Drkn'), 49)
	list1.putObject(cID('GEfc'), desc3)
	desc1.putList(cID('GEfs'), list1)
	app.executeAction(1195730531, desc1, dialog_mode)

	# Levels - Auto Tone
	auto_tone()

	# Levels - Auto Contrast
	auto_contrast()

	# Set - Blending Multiply
	blend_multiply()

	# Set
	set_opacity(50)

	# Move
	move_layer(5, 261)

	# Select
	select_bg()

	# Layer Via Copy - Background Copy 8
	app.executeAction(sID('copyToLayer'), ps.ActionDescriptor(), dialog_mode)

	# Move
	move_layer(12, 263)

	# Reset
	reset_colors()

	# Filter Gallery - Photocopy
	desc1 = ps.ActionDescriptor()
	desc1.putEnumerated(cID('GEfk'), cID('GEft'), cID('Phtc'))
	desc1.putInteger(cID('Dtl '), 2)
	desc1.putInteger(cID('Drkn'), 5)
	app.executeAction(1195730531, desc1, dialog_mode)

	# Set
	blend_multiply()

	# Layer Via Copy - Background Copy 9
	app.executeAction(sID('copyToLayer'), ps.ActionDescriptor(), dialog_mode)

	# Transform
	desc1 = ps.ActionDescriptor()
	ref1 = ps.ActionReference()
	ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
	desc1.putReference(cID('null'), ref1)
	desc1.putEnumerated(cID('FTcs'), cID('QCSt'), sID("QCSAverage"))
	desc2 = ps.ActionDescriptor()
	desc2.putUnitDouble(cID('Hrzn'), cID('#Pxl'), 0)
	desc2.putUnitDouble(cID('Vrtc'), cID('#Pxl'), 0)
	desc1.putObject(cID('Ofst'), cID('Ofst'), desc2)
	desc1.putUnitDouble(cID('Wdth'), cID('#Prc'), 110)
	desc1.putUnitDouble(cID('Hght'), cID('#Prc'), 110)
	desc1.putBoolean(cID('Lnkd'), True)
	desc1.putEnumerated(cID('Intr'), cID('Intp'), cID('Bcbc'))
	app.executeAction(cID('Trnf'), desc1, dialog_mode)

	# Select
	select_layer("Background copy 8", 263)

	# Transform
	desc1 = ps.ActionDescriptor()
	ref1 = ps.ActionReference()
	ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
	desc1.putReference(cID('null'), ref1)
	desc1.putEnumerated(cID('FTcs'), cID('QCSt'), sID("QCSAverage"))
	desc2 = ps.ActionDescriptor()
	desc2.putUnitDouble(cID('Hrzn'), cID('#Pxl'), -2.27373675443232e-13)
	desc2.putUnitDouble(cID('Vrtc'), cID('#Pxl'), 0)
	desc1.putObject(cID('Ofst'), cID('Ofst'), desc2)
	desc1.putUnitDouble(cID('Wdth'), cID('#Prc'), 90)
	desc1.putUnitDouble(cID('Hght'), cID('#Prc'), 90)
	desc1.putBoolean(cID('Lnkd'), True)
	desc1.putEnumerated(cID('Intr'), cID('Intp'), cID('Bcbc'))
	app.executeAction(cID('Trnf'), desc1, dialog_mode)

	# Select
	select_layers("Background copy 9", [263, 264])

	# Set
	set_opacity(10)

	# Move
	move_layer(8, [263, 264])

	# Select
	select_layer("Background copy 7", 250)

	# Select
	select_layers("Layer 2", [
		250, 240, 242, 261, 244, 246, 263, 264, 258, 255
	])

	# Set
	blend_linear_burn()

	# Select
	select_layer("Color Fill 1", 238)

	# Make
	new_layer(268)

	# Fill - 50% Gray
	desc1 = ps.ActionDescriptor()
	desc1.putEnumerated(cID('Usng'), cID('FlCn'), cID('Gry '))
	desc1.putUnitDouble(cID('Opct'), cID('#Prc'), 100)
	desc1.putEnumerated(cID('Md  '), cID('BlnM'), cID('Nrml'))
	app.executeAction(cID('Fl  '), desc1, dialog_mode)

	# Filter Gallery - Texturizer
	desc1 = ps.ActionDescriptor()
	desc1.putEnumerated(cID('GEfk'), cID('GEft'), cID('Txtz'))
	desc1.putEnumerated(cID('TxtT'), cID('TxtT'), cID('TxSt'))
	desc1.putInteger(cID('Scln'), 200)
	desc1.putInteger(cID('Rlf '), 4)
	desc1.putEnumerated(cID('LghD'), cID('LghD'), cID('LDTp'))
	desc1.putBoolean(cID('InvT'), False)
	app.executeAction(1195730531, desc1, dialog_mode)

	# Set - Blending Soft Light
	blend_soft_light()

	# Select
	select_layer("Layer 4", 268)

	# Make
	new_layer(269)

	# Fill - Foreground Color
	desc1 = ps.ActionDescriptor()
	desc1.putEnumerated(cID('Usng'), cID('FlCn'), cID('FrgC'))
	desc1.putUnitDouble(cID('Opct'), cID('#Prc'), 100)
	desc1.putEnumerated(cID('Md  '), cID('BlnM'), cID('Nrml'))
	app.executeAction(cID('Fl  '), desc1, dialog_mode)

	# Add Noise
	desc1 = ps.ActionDescriptor()
	desc1.putEnumerated(cID('Dstr'), cID('Dstr'), cID('Gsn '))
	desc1.putUnitDouble(cID('Nose'), cID('#Prc'), 25)
	desc1.putBoolean(cID('Mnch'), True)
	desc1.putInteger(cID('FlRs'), 1315132)
	app.executeAction(sID('addNoise'), desc1, dialog_mode)
	app.activeDocument.activeLayer.opacity = 40

	# Set
	blend_screen()

	# Levels Adjustment
	desc1 = ps.ActionDescriptor()
	desc1.putEnumerated(sID("presetKind"), sID("presetKindType"), sID("presetKindCustom"))
	list1 = ps.ActionList()
	desc2 = ps.ActionDescriptor()
	ref1 = ps.ActionReference()
	ref1.putEnumerated(cID('Chnl'), cID('Chnl'), cID('Cmps'))
	desc2.putReference(cID('Chnl'), ref1)
	list2 = ps.ActionList()
	list2.putInteger(0)
	list2.putInteger(90)
	desc2.putList(cID('Inpt'), list2)
	list1.putObject(cID('LvlA'), desc2)
	desc1.putList(cID('Adjs'), list1)
	app.executeAction(cID('Lvls'), desc1, dialog_mode)

	# Select
	select_layer("Background copy 4", 246)

	# Move
	move_layer(6, 246)

	# Select
	select_layer("Background copy 3", 244)

	# Set
	set_opacity(20)

	# Select
	select_layer("Layer 3", 258)

	# Select
	select_layers("Layer 2", [258, 255])

	# Set
	set_opacity(40)

	# Select
	select_layer("Background copy 5", 252)

	# Reset
	reset_colors()

	# Make - Gradient Map
	desc1 = ps.ActionDescriptor()
	ref1 = ps.ActionReference()
	ref1.putClass(cID('AdjL'))
	desc1.putReference(cID('null'), ref1)
	desc2 = ps.ActionDescriptor()
	desc3 = ps.ActionDescriptor()
	desc4 = ps.ActionDescriptor()
	desc4.putString(cID('Nm  '), "Foreground to Background")
	desc4.putEnumerated(cID('GrdF'), cID('GrdF'), cID('CstS'))
	desc4.putDouble(cID('Intr'), 4096)
	list1 = ps.ActionList()
	desc5 = ps.ActionDescriptor()
	desc6 = ps.ActionDescriptor()
	desc6.putDouble(cID('Rd  '), 0)
	desc6.putDouble(cID('Grn '), 0)
	desc6.putDouble(cID('Bl  '), 0)
	desc5.putObject(cID('Clr '), sID("RGBColor"), desc6)
	desc5.putEnumerated(cID('Type'), cID('Clry'), cID('UsrS'))
	desc5.putInteger(cID('Lctn'), 0)
	desc5.putInteger(cID('Mdpn'), 50)
	list1.putObject(cID('Clrt'), desc5)
	desc7 = ps.ActionDescriptor()
	desc8 = ps.ActionDescriptor()
	desc8.putDouble(cID('Rd  '), 255)
	desc8.putDouble(cID('Grn '), 255)
	desc8.putDouble(cID('Bl  '), 255)
	desc7.putObject(cID('Clr '), sID("RGBColor"), desc8)
	desc7.putEnumerated(cID('Type'), cID('Clry'), cID('UsrS'))
	desc7.putInteger(cID('Lctn'), 4096)
	desc7.putInteger(cID('Mdpn'), 50)
	list1.putObject(cID('Clrt'), desc7)
	desc4.putList(cID('Clrs'), list1)
	list2 = ps.ActionList()
	desc9 = ps.ActionDescriptor()
	desc9.putUnitDouble(cID('Opct'), cID('#Prc'), 100)
	desc9.putInteger(cID('Lctn'), 0)
	desc9.putInteger(cID('Mdpn'), 50)
	list2.putObject(cID('TrnS'), desc9)
	desc10 = ps.ActionDescriptor()
	desc10.putUnitDouble(cID('Opct'), cID('#Prc'), 100)
	desc10.putInteger(cID('Lctn'), 4096)
	desc10.putInteger(cID('Mdpn'), 50)
	list2.putObject(cID('TrnS'), desc10)
	desc4.putList(cID('Trns'), list2)
	desc3.putObject(cID('Grad'), cID('Grdn'), desc4)
	desc2.putObject(cID('Type'), cID('GdMp'), desc3)
	desc1.putObject(cID('Usng'), cID('AdjL'), desc2)
	app.executeAction(cID('Mk  '), desc1, dialog_mode)

	# Set
	blend_soft_light()

	# Set
	set_opacity(20)

	# Make - Levels Adjustment Layer
	desc1 = ps.ActionDescriptor()
	ref1 = ps.ActionReference()
	ref1.putClass(cID('AdjL'))
	desc1.putReference(cID('null'), ref1)
	desc2 = ps.ActionDescriptor()
	desc3 = ps.ActionDescriptor()
	desc3.putEnumerated(sID("presetKind"), sID("presetKindType"), sID("presetKindDefault"))
	desc2.putObject(cID('Type'), cID('Lvls'), desc3)
	desc1.putObject(cID('Usng'), cID('AdjL'), desc2)
	app.executeAction(cID('Mk  '), desc1, dialog_mode)

	# Set - Levels Adjustment Layer Settings
	desc1 = ps.ActionDescriptor()
	ref1 = ps.ActionReference()
	ref1.putEnumerated(cID('AdjL'), cID('Ordn'), cID('Trgt'))
	desc1.putReference(cID('null'), ref1)
	desc2 = ps.ActionDescriptor()
	desc2.putEnumerated(sID("presetKind"), sID("presetKindType"), sID("presetKindCustom"))
	list1 = ps.ActionList()
	desc3 = ps.ActionDescriptor()
	ref2 = ps.ActionReference()
	ref2.putEnumerated(cID('Chnl'), cID('Chnl'), cID('Cmps'))
	desc3.putReference(cID('Chnl'), ref2)
	desc3.putDouble(cID('Gmm '), 0.8)
	list2 = ps.ActionList()
	list2.putInteger(30)
	list2.putInteger(250)
	desc3.putList(cID('Inpt'), list2)
	list1.putObject(cID('LvlA'), desc3)
	desc2.putList(cID('Adjs'), list1)
	desc1.putObject(cID('T   '), cID('Lvls'), desc2)
	app.executeAction(cID('setd'), desc1, dialog_mode)

	# Select
	select_layer("Background copy 6", 112)

	# Set
	set_opacity(40)

	# Select
	select_bg()

	# Layer Via Copy - Background Copy 10
	app.executeAction(sID('copyToLayer'), ps.ActionDescriptor(), dialog_mode)

	# Move
	move_layer(18, 121)

	# Reset
	reset_colors()

	# Filter Gallery - Graphic Pen
	desc1 = ps.ActionDescriptor()
	desc1.putEnumerated(cID('GEfk'), cID('GEft'), cID('GraP'))
	desc1.putInteger(cID('StrL'), 15)
	desc1.putInteger(cID('LgDr'), 50)
	desc1.putEnumerated(cID('SDir'), cID('StrD'), cID('SDRD'))
	app.executeAction(1195730531, desc1, dialog_mode)

	# Set
	blend_overlay()

	# Set
	set_opacity(30)

	# Move
	move_layer(5, 121)

	# Select
	select_bg()

	# Layer Via Copy - Background copy 11
	app.executeAction(sID('copyToLayer'), ps.ActionDescriptor(), dialog_mode)

	# Move
	move_layer(16, 127)

	# Set
	blend_color()

	"""

	# Make - Hue/Saturation Adjustment
	desc1 = ps.ActionDescriptor()
	ref1 = ps.ActionReference()
	ref1.putClass(cID('AdjL'))
	desc1.putReference(cID('null'), ref1)
	desc2 = ps.ActionDescriptor()
	desc3 = ps.ActionDescriptor()
	desc3.putEnumerated(sID("presetKind"), sID("presetKindType"), sID("presetKindDefault"))
	desc3.putBoolean(cID('Clrz'), False)
	desc2.putObject(cID('Type'), cID('HStr'), desc3)
	desc1.putObject(cID('Usng'), cID('AdjL'), desc2)
	app.executeAction(cID('Mk  '), desc1, dialog_mode)

	# Create Clipping Mask
	desc1 = ps.ActionDescriptor()
	ref1 = ps.ActionReference()
	ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
	desc1.putReference(cID('null'), ref1)
	app.executeAction(sID('groupEvent'), desc1, dialog_mode)

	# Select
	select_layers("Background copy 11", [127, 128])

	# Move
	move_layer(16, [127, 128])

	# Select
	select_layer("Levels 1", 119)

	# Make - Hue/Saturation Adjustment Layer
	desc1 = ps.ActionDescriptor()
	ref1 = ps.ActionReference()
	ref1.putClass(cID('AdjL'))
	desc1.putReference(cID('null'), ref1)
	desc2 = ps.ActionDescriptor()
	desc3 = ps.ActionDescriptor()
	desc3.putEnumerated(sID("presetKind"), sID("presetKindType"), sID("presetKindDefault"))
	desc3.putBoolean(cID('Clrz'), False)
	desc2.putObject(cID('Type'), cID('HStr'), desc3)
	desc1.putObject(cID('Usng'), cID('AdjL'), desc2)
	app.executeAction(cID('Mk  '), desc1, dialog_mode)

	# Merge Visible
	desc1 = ps.ActionDescriptor()
	desc1.putBoolean(cID('Dplc'), True)
	app.executeAction(sID('mergeVisible'), desc1, dialog_mode)

	# Desaturate
	def step182():

		app.executeAction(cID('Dstt'), ps.ActionDescriptor(), dialog_mode)

	# High Pass
	def step183():

		desc1 = ps.ActionDescriptor()
		desc1.putUnitDouble(cID('Rds '), cID('#Pxl'), 1)
		app.executeAction(sID('highPass'), desc1, dialog_mode)

	# Set
	def step184():

		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		desc2 = ps.ActionDescriptor()
		desc2.putEnumerated(cID('Md  '), cID('BlnM'), sID("vividLight"))
		desc1.putObject(cID('T   '), cID('Lyr '), desc2)
		app.executeAction(cID('setd'), desc1, dialog_mode)

	# Select
	def step185():

		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Color Fill 1")
		desc1.putReference(cID('null'), ref1)
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(90)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Select
	def step186():

		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Layer 6")
		desc1.putReference(cID('null'), ref1)
		desc1.putEnumerated(sID("selectionModifier"), sID("selectionModifierType"), sID("addToSelectionContinuous"))
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(90)
		list1.putInteger(116)
		list1.putInteger(117)
		list1.putInteger(102)
		list1.putInteger(121)
		list1.putInteger(92)
		list1.putInteger(98)
		list1.putInteger(94)
		list1.putInteger(112)
		list1.putInteger(96)
		list1.putInteger(114)
		list1.putInteger(115)
		list1.putInteger(110)
		list1.putInteger(107)
		list1.putInteger(104)
		list1.putInteger(127)
		list1.putInteger(128)
		list1.putInteger(118)
		list1.putInteger(119)
		list1.putInteger(130)
		list1.putInteger(131)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Make
	def step187():

		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putClass(sID("layerSection"))
		desc1.putReference(cID('null'), ref1)
		ref2 = ps.ActionReference()
		ref2.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('From'), ref2)
		desc2 = ps.ActionDescriptor()
		desc2.putString(cID('Nm  '), "Pencil Sketch")
		desc1.putObject(cID('Usng'), sID("layerSection"), desc2)
		desc1.putInteger(sID("layerSectionStart"), 136)
		desc1.putInteger(sID("layerSectionEnd"), 137)
		desc1.putString(cID('Nm  '), "Pencil Sketch")
		app.executeAction(cID('Mk  '), desc1, dialog_mode)

	# Make
	def step188():

		desc1 = ps.ActionDescriptor()
		desc1.putClass(cID('Nw  '), cID('Chnl'))
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Chnl'), cID('Chnl'), cID('Msk '))
		desc1.putReference(cID('At  '), ref1)
		desc1.putEnumerated(cID('Usng'), cID('UsrM'), cID('RvlA'))
		app.executeAction(cID('Mk  '), desc1, dialog_mode)

	# Set
	def step189():

		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		desc2 = ps.ActionDescriptor()
		desc2.putBoolean(cID('Usrs'), False)
		desc1.putObject(cID('T   '), cID('Lyr '), desc2)
		app.executeAction(cID('setd'), desc1, dialog_mode)

	# Select
	def step190():

		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Layer 1")
		desc1.putReference(cID('null'), ref1)
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(139)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Delete
	def step191():

		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		list1 = ps.ActionList()
		list1.putInteger(139)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('Dlt '), desc1, dialog_mode)

	# Select Background
	def step343(): select_bg()
	
	"""

	if not draft_sketch:
		hide_layer("Layer 2")
		hide_layer("Layer 3")

	if not rough_sketch:
		hide_layer("Background copy 3")
		hide_layer("Background copy 6")
		hide_layer("Background copy 8")
		hide_layer("Background copy 9")

	if not colored:
		hide_layer("Background copy 11")

	# Flatten
	app.executeAction(cID("FltI"), None, dialog_mode)
