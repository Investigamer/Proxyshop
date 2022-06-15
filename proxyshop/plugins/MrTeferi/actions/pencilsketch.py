"""
Pencil Sketchify Action Module
"""
import time
import photoshop.api as ps
app = ps.Application()
cID = app.charIDToTypeID
sID = app.stringIDToTypeID


def run(draft_sketch=False, rough_sketch=False, colored=True):
	"""
	Pencil Sketchify Steps
	"""

	# Purge
	def step1(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		desc1.putEnumerated(cID('null'), cID('PrgI'), cID('Al  '))
		app.executeAction(cID('Prge'), desc1, dialog_mode)

	# Reset
	def step2(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putProperty(cID('Clr '), cID('Clrs'))
		desc1.putReference(cID('null'), ref1)
		app.executeAction(cID('Rset'), desc1, dialog_mode)

	# Make
	def step3(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putClass(cID('Lyr '))
		desc1.putReference(cID('null'), ref1)
		desc1.putInteger(cID('LyrI'), 139)
		app.executeAction(cID('Mk  '), desc1, dialog_mode)

	# Select
	def step4(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Background")
		desc1.putReference(cID('null'), ref1)
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(1)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Make
	def step5(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putClass(sID("contentLayer"))
		desc1.putReference(cID('null'), ref1)
		desc2 = ps.ActionDescriptor()
		desc3 = ps.ActionDescriptor()
		desc4 = ps.ActionDescriptor()
		desc4.putDouble(cID('Rd  '), 242.24902421236)
		desc4.putDouble(cID('Grn '), 242.24902421236)
		desc4.putDouble(cID('Bl  '), 242.24902421236)
		desc3.putObject(cID('Clr '), sID("RGBColor"), desc4)
		desc2.putObject(cID('Type'), sID("solidColorLayer"), desc3)
		desc1.putObject(cID('Usng'), sID("contentLayer"), desc2)
		app.executeAction(cID('Mk  '), desc1, dialog_mode)

	# Select
	def step6(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Background")
		desc1.putReference(cID('null'), ref1)
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(1)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Layer Via Copy
	def step7(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		app.executeAction(sID('copyToLayer'), ps.ActionDescriptor(), dialog_mode)

	# Move
	def step8(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		ref2 = ps.ActionReference()
		ref2.putIndex(cID('Lyr '), 3)
		desc1.putReference(cID('T   '), ref2)
		desc1.putBoolean(cID('Adjs'), False)
		desc1.putInteger(cID('Vrsn'), 5)
		list1 = ps.ActionList()
		list1.putInteger(240)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('move'), desc1, dialog_mode)

	# Reset
	def step9(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putProperty(cID('Clr '), cID('Clrs'))
		desc1.putReference(cID('null'), ref1)
		app.executeAction(cID('Rset'), desc1, dialog_mode)

	# Filter Gallery
	def step10(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		desc1.putEnumerated(cID('GEfk'), cID('GEft'), cID('Phtc'))
		desc1.putInteger(cID('Dtl '), 2)
		desc1.putInteger(cID('Drkn'), 5)
		app.executeAction(1195730531, desc1, dialog_mode)

	# Set
	def step11(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		desc2 = ps.ActionDescriptor()
		desc2.putEnumerated(cID('Md  '), cID('BlnM'), cID('Mltp'))
		desc1.putObject(cID('T   '), cID('Lyr '), desc2)
		app.executeAction(cID('setd'), desc1, dialog_mode)

	# Select
	def step12(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Background")
		desc1.putReference(cID('null'), ref1)
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(1)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Layer Via Copy
	def step13(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		app.executeAction(sID('copyToLayer'), ps.ActionDescriptor(), dialog_mode)

	# Move
	def step14(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		ref2 = ps.ActionReference()
		ref2.putIndex(cID('Lyr '), 4)
		desc1.putReference(cID('T   '), ref2)
		desc1.putBoolean(cID('Adjs'), False)
		desc1.putInteger(cID('Vrsn'), 5)
		list1 = ps.ActionList()
		list1.putInteger(242)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('move'), desc1, dialog_mode)

	# Reset
	def step15(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putProperty(cID('Clr '), cID('Clrs'))
		desc1.putReference(cID('null'), ref1)
		app.executeAction(cID('Rset'), desc1, dialog_mode)

	# Filter Gallery
	def step16(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
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

	# Set
	def step17(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		desc2 = ps.ActionDescriptor()
		desc2.putEnumerated(cID('Md  '), cID('BlnM'), cID('Mltp'))
		desc1.putObject(cID('T   '), cID('Lyr '), desc2)
		app.executeAction(cID('setd'), desc1, dialog_mode)

	# Select
	def step18(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Background")
		desc1.putReference(cID('null'), ref1)
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(1)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Layer Via Copy
	def step19(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		app.executeAction(sID('copyToLayer'), ps.ActionDescriptor(), dialog_mode)

	# Move
	def step20(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		ref2 = ps.ActionReference()
		ref2.putIndex(cID('Lyr '), 5)
		desc1.putReference(cID('T   '), ref2)
		desc1.putBoolean(cID('Adjs'), False)
		desc1.putInteger(cID('Vrsn'), 5)
		list1 = ps.ActionList()
		list1.putInteger(244)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('move'), desc1, dialog_mode)

	# Reset
	def step21(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putProperty(cID('Clr '), cID('Clrs'))
		desc1.putReference(cID('null'), ref1)
		app.executeAction(cID('Rset'), desc1, dialog_mode)

	# Filter Gallery
	def step22(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
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

	# Set
	def step23(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		desc2 = ps.ActionDescriptor()
		desc2.putEnumerated(cID('Md  '), cID('BlnM'), cID('Mltp'))
		desc1.putObject(cID('T   '), cID('Lyr '), desc2)
		app.executeAction(cID('setd'), desc1, dialog_mode)

	# Set
	def step24(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		desc2 = ps.ActionDescriptor()
		desc2.putUnitDouble(cID('Opct'), cID('#Prc'), 25)
		desc1.putObject(cID('T   '), cID('Lyr '), desc2)
		app.executeAction(cID('setd'), desc1, dialog_mode)

	# Select
	def step25(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Background")
		desc1.putReference(cID('null'), ref1)
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(1)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Layer Via Copy
	def step26(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		app.executeAction(sID('copyToLayer'), ps.ActionDescriptor(), dialog_mode)

	# Move
	def step27(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		ref2 = ps.ActionReference()
		ref2.putIndex(cID('Lyr '), 6)
		desc1.putReference(cID('T   '), ref2)
		desc1.putBoolean(cID('Adjs'), False)
		desc1.putInteger(cID('Vrsn'), 5)
		list1 = ps.ActionList()
		list1.putInteger(246)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('move'), desc1, dialog_mode)

	# Reset
	def step28(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putProperty(cID('Clr '), cID('Clrs'))
		desc1.putReference(cID('null'), ref1)
		app.executeAction(cID('Rset'), desc1, dialog_mode)

	# Filter Gallery
	def step29(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		desc1.putEnumerated(cID('GEfk'), cID('GEft'), cID('GlwE'))
		desc1.putInteger(cID('EdgW'), 1)
		desc1.putInteger(cID('EdgB'), 20)
		desc1.putInteger(cID('Smth'), 15)
		app.executeAction(1195730531, desc1, dialog_mode)

	# Desaturate
	def step30(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		app.executeAction(cID('Dstt'), ps.ActionDescriptor(), dialog_mode)

	# Levels
	def step31(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		desc1.putBoolean(cID('Auto'), True)
		app.executeAction(cID('Lvls'), desc1, dialog_mode)

	# Levels
	def step32(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		desc1.putBoolean(cID('AuCo'), True)
		app.executeAction(cID('Lvls'), desc1, dialog_mode)

	# Levels
	def step33(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
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
	def step34(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		app.executeAction(cID('Invr'), ps.ActionDescriptor(), dialog_mode)

	# Set
	def step35(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		desc2 = ps.ActionDescriptor()
		desc2.putEnumerated(cID('Md  '), cID('BlnM'), cID('Mltp'))
		desc1.putObject(cID('T   '), cID('Lyr '), desc2)
		app.executeAction(cID('setd'), desc1, dialog_mode)

	# Select
	def step36(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Background")
		desc1.putReference(cID('null'), ref1)
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(1)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Layer Via Copy
	def step37(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		app.executeAction(sID('copyToLayer'), ps.ActionDescriptor(), dialog_mode)

	# Move
	def step38(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		ref2 = ps.ActionReference()
		ref2.putIndex(cID('Lyr '), 7)
		desc1.putReference(cID('T   '), ref2)
		desc1.putBoolean(cID('Adjs'), False)
		desc1.putInteger(cID('Vrsn'), 5)
		list1 = ps.ActionList()
		list1.putInteger(248)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('move'), desc1, dialog_mode)

	# Layer Via Copy
	def step39(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		app.executeAction(sID('copyToLayer'), ps.ActionDescriptor(), dialog_mode)

	# Invert
	def step40(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		app.executeAction(cID('Invr'), ps.ActionDescriptor(), dialog_mode)

	# Gaussian Blur
	def step41(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		desc1.putUnitDouble(cID('Rds '), cID('#Pxl'), 50)
		app.executeAction(sID('gaussianBlur'), desc1, dialog_mode)

	# Set
	def step42(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		desc2 = ps.ActionDescriptor()
		desc2.putEnumerated(cID('Md  '), cID('BlnM'), cID('CDdg'))
		desc1.putObject(cID('T   '), cID('Lyr '), desc2)
		app.executeAction(cID('setd'), desc1, dialog_mode)

	# Select
	def step43(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Background copy 5")
		desc1.putReference(cID('null'), ref1)
		desc1.putEnumerated(sID("selectionModifier"), sID("selectionModifierType"), sID("addToSelection"))
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(248)
		list1.putInteger(249)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Merge Layers
	def step44(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		app.executeAction(sID('mergeLayersNew'), desc1, dialog_mode)

	# Desaturate
	def step45(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		app.executeAction(cID('Dstt'), ps.ActionDescriptor(), dialog_mode)

	# Layer Via Copy
	def step46(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		app.executeAction(sID('copyToLayer'), ps.ActionDescriptor(), dialog_mode)

	# Reset
	def step47(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putProperty(cID('Clr '), cID('Clrs'))
		desc1.putReference(cID('null'), ref1)
		app.executeAction(cID('Rset'), desc1, dialog_mode)

	# Filter Gallery
	def step48(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		desc1.putEnumerated(cID('GEfk'), cID('GEft'), cID('GlwE'))
		desc1.putInteger(cID('EdgW'), 1)
		desc1.putInteger(cID('EdgB'), 20)
		desc1.putInteger(cID('Smth'), 15)
		app.executeAction(1195730531, desc1, dialog_mode)

	# Invert
	def step49(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		app.executeAction(cID('Invr'), ps.ActionDescriptor(), dialog_mode)

	# Set
	def step50(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		desc2 = ps.ActionDescriptor()
		desc2.putEnumerated(cID('Md  '), cID('BlnM'), cID('Mltp'))
		desc1.putObject(cID('T   '), cID('Lyr '), desc2)
		app.executeAction(cID('setd'), desc1, dialog_mode)

	# Set
	def step51(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		desc2 = ps.ActionDescriptor()
		desc2.putUnitDouble(cID('Opct'), cID('#Prc'), 80)
		desc1.putObject(cID('T   '), cID('Lyr '), desc2)
		app.executeAction(cID('setd'), desc1, dialog_mode)

	# Select
	def step52(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Background copy 6")
		desc1.putReference(cID('null'), ref1)
		desc1.putEnumerated(sID("selectionModifier"), sID("selectionModifierType"), sID("addToSelection"))
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(249)
		list1.putInteger(250)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Merge Layers
	def step53(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		app.executeAction(sID('mergeLayersNew'), desc1, dialog_mode)

	# Select
	def step54(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Background")
		desc1.putReference(cID('null'), ref1)
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(1)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Layer Via Copy
	def step55(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		app.executeAction(sID('copyToLayer'), ps.ActionDescriptor(), dialog_mode)

	# Move
	def step56(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		ref2 = ps.ActionReference()
		ref2.putIndex(cID('Lyr '), 8)
		desc1.putReference(cID('T   '), ref2)
		desc1.putBoolean(cID('Adjs'), False)
		desc1.putInteger(cID('Vrsn'), 5)
		list1 = ps.ActionList()
		list1.putInteger(252)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('move'), desc1, dialog_mode)

	# Desaturate
	def step57(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		app.executeAction(cID('Dstt'), ps.ActionDescriptor(), dialog_mode)

	# High Pass
	def step58(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		desc1.putUnitDouble(cID('Rds '), cID('#Pxl'), 30)
		app.executeAction(sID('highPass'), desc1, dialog_mode)

	# Set
	def step59(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		desc2 = ps.ActionDescriptor()
		desc2.putEnumerated(cID('Md  '), cID('BlnM'), sID("linearLight"))
		desc1.putObject(cID('T   '), cID('Lyr '), desc2)
		app.executeAction(cID('setd'), desc1, dialog_mode)

	# Set
	def step60(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
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
	def step61(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		desc2 = ps.ActionDescriptor()
		desc2.putUnitDouble(cID('Opct'), cID('#Prc'), 50)
		desc1.putObject(cID('T   '), cID('Lyr '), desc2)
		app.executeAction(cID('setd'), desc1, dialog_mode)

	# Select
	def step62(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Background")
		desc1.putReference(cID('null'), ref1)
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(1)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Layer Via Copy
	def step63(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		app.executeAction(sID('copyToLayer'), ps.ActionDescriptor(), dialog_mode)

	# Move
	def step64(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		ref2 = ps.ActionReference()
		ref2.putIndex(cID('Lyr '), 9)
		desc1.putReference(cID('T   '), ref2)
		desc1.putBoolean(cID('Adjs'), False)
		desc1.putInteger(cID('Vrsn'), 5)
		list1 = ps.ActionList()
		list1.putInteger(254)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('move'), desc1, dialog_mode)

	# Reset
	def step65(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putProperty(cID('Clr '), cID('Clrs'))
		desc1.putReference(cID('null'), ref1)
		app.executeAction(cID('Rset'), desc1, dialog_mode)

	# Filter Gallery
	def step66(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		desc1.putEnumerated(cID('GEfk'), cID('GEft'), cID('Ct  '))
		desc1.putInteger(cID('NmbL'), 8)
		desc1.putInteger(cID('EdgS'), 10)
		desc1.putInteger(cID('EdgF'), 1)
		app.executeAction(1195730531, desc1, dialog_mode)

	# Desaturate
	def step67(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		app.executeAction(cID('Dstt'), ps.ActionDescriptor(), dialog_mode)

	# Levels
	def step68(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		desc1.putBoolean(cID('Auto'), True)
		app.executeAction(cID('Lvls'), desc1, dialog_mode)

	# Levels
	def step69(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		desc1.putBoolean(cID('AuCo'), True)
		app.executeAction(cID('Lvls'), desc1, dialog_mode)

	# Color Range
	def step70(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		desc1.putEnumerated(cID('Clrs'), cID('Clrs'), cID('Mdtn'))
		desc1.putInteger(sID("midtonesFuzziness"), 40)
		desc1.putInteger(sID("midtonesLowerLimit"), 105)
		desc1.putInteger(sID("midtonesUpperLimit"), 150)
		desc1.putInteger(sID("colorModel"), 0)
		app.executeAction(sID('colorRange'), desc1, dialog_mode)

	# Layer Via Copy
	def step71(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		app.executeAction(sID('copyToLayer'), ps.ActionDescriptor(), dialog_mode)

	# Find Edges
	def step72(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		app.executeAction(sID('findEdges'), ps.ActionDescriptor(), dialog_mode)

	# Hide
	def step73(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		list1 = ps.ActionList()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Background copy 6")
		list1.putReference(ref1)
		desc1.putList(cID('null'), list1)
		app.executeAction(cID('Hd  '), desc1, dialog_mode)

	# Hide
	def step74(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		list1 = ps.ActionList()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		list1.putReference(ref1)
		desc1.putList(cID('null'), list1)
		app.executeAction(cID('Hd  '), desc1, dialog_mode)

	# Select
	def step75(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Background")
		desc1.putReference(cID('null'), ref1)
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(1)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Layer Via Copy
	def step76(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		app.executeAction(sID('copyToLayer'), ps.ActionDescriptor(), dialog_mode)

	# Move
	def step77(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		ref2 = ps.ActionReference()
		ref2.putIndex(cID('Lyr '), 9)
		desc1.putReference(cID('T   '), ref2)
		desc1.putBoolean(cID('Adjs'), False)
		desc1.putInteger(cID('Vrsn'), 5)
		list1 = ps.ActionList()
		list1.putInteger(257)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('move'), desc1, dialog_mode)

	# Reset
	def step78(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putProperty(cID('Clr '), cID('Clrs'))
		desc1.putReference(cID('null'), ref1)
		app.executeAction(cID('Rset'), desc1, dialog_mode)

	# Filter Gallery
	def step79(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		desc1.putEnumerated(cID('GEfk'), cID('GEft'), cID('Ct  '))
		desc1.putInteger(cID('NmbL'), 8)
		desc1.putInteger(cID('EdgS'), 8)
		desc1.putInteger(cID('EdgF'), 1)
		app.executeAction(1195730531, desc1, dialog_mode)

	# Desaturate
	def step80(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		app.executeAction(cID('Dstt'), ps.ActionDescriptor(), dialog_mode)

	# Levels
	def step81(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		desc1.putBoolean(cID('Auto'), True)
		app.executeAction(cID('Lvls'), desc1, dialog_mode)

	# Levels
	def step82(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		desc1.putBoolean(cID('AuCo'), True)
		app.executeAction(cID('Lvls'), desc1, dialog_mode)

	# Color Range
	def step83(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		desc1.putEnumerated(cID('Clrs'), cID('Clrs'), cID('Mdtn'))
		desc1.putInteger(sID("midtonesFuzziness"), 40)
		desc1.putInteger(sID("midtonesLowerLimit"), 105)
		desc1.putInteger(sID("midtonesUpperLimit"), 150)
		desc1.putInteger(sID("colorModel"), 0)
		app.executeAction(sID('colorRange'), desc1, dialog_mode)

	# Layer Via Copy
	def step84(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		app.executeAction(sID('copyToLayer'), ps.ActionDescriptor(), dialog_mode)

	# Find Edges
	def step85(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		app.executeAction(sID('findEdges'), ps.ActionDescriptor(), dialog_mode)

	# Select
	def step86(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Background copy 8")
		desc1.putReference(cID('null'), ref1)
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(257)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Select
	def step87(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Background copy 6")
		desc1.putReference(cID('null'), ref1)
		desc1.putEnumerated(sID("selectionModifier"), sID("selectionModifierType"), sID("addToSelection"))
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(257)
		list1.putInteger(254)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Delete
	def step88(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		list1 = ps.ActionList()
		list1.putInteger(257)
		list1.putInteger(254)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('Dlt '), desc1, dialog_mode)

	# Select
	def step89(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Layer 2")
		desc1.putReference(cID('null'), ref1)
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(255)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Show
	def step90(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		list1 = ps.ActionList()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		list1.putReference(ref1)
		desc1.putList(cID('null'), list1)
		app.executeAction(cID('Shw '), desc1, dialog_mode)

	# Select
	def step91(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Layer 3")
		desc1.putReference(cID('null'), ref1)
		desc1.putEnumerated(sID("selectionModifier"), sID("selectionModifierType"), sID("addToSelection"))
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(258)
		list1.putInteger(255)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Set
	def step92(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		desc2 = ps.ActionDescriptor()
		desc2.putEnumerated(cID('Md  '), cID('BlnM'), cID('Mltp'))
		desc1.putObject(cID('T   '), cID('Lyr '), desc2)
		app.executeAction(cID('setd'), desc1, dialog_mode)

	# Set
	def step93(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		desc2 = ps.ActionDescriptor()
		desc2.putUnitDouble(cID('Opct'), cID('#Prc'), 30)
		desc1.putObject(cID('T   '), cID('Lyr '), desc2)
		app.executeAction(cID('setd'), desc1, dialog_mode)

	# Select
	def step94(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Background copy 3")
		desc1.putReference(cID('null'), ref1)
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(244)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Set
	def step95(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		desc2 = ps.ActionDescriptor()
		desc2.putUnitDouble(cID('Opct'), cID('#Prc'), 30)
		desc1.putObject(cID('T   '), cID('Lyr '), desc2)
		app.executeAction(cID('setd'), desc1, dialog_mode)

	# Select
	def step96(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Background copy 7")
		desc1.putReference(cID('null'), ref1)
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(250)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Move
	def step97(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		ref2 = ps.ActionReference()
		ref2.putIndex(cID('Lyr '), 2)
		desc1.putReference(cID('T   '), ref2)
		desc1.putBoolean(cID('Adjs'), False)
		desc1.putInteger(cID('Vrsn'), 5)
		list1 = ps.ActionList()
		list1.putInteger(250)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('move'), desc1, dialog_mode)

	# Select
	def step98(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Background copy 5")
		desc1.putReference(cID('null'), ref1)
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(252)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Move
	def step99(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		ref2 = ps.ActionReference()
		ref2.putIndex(cID('Lyr '), 10)
		desc1.putReference(cID('T   '), ref2)
		desc1.putBoolean(cID('Adjs'), False)
		desc1.putInteger(cID('Vrsn'), 5)
		list1 = ps.ActionList()
		list1.putInteger(252)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('move'), desc1, dialog_mode)

	# Hide
	def step100(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		list1 = ps.ActionList()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Background copy 7")
		list1.putReference(ref1)
		desc1.putList(cID('null'), list1)
		app.executeAction(cID('Hd  '), desc1, dialog_mode)

	# Show
	def step101(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		list1 = ps.ActionList()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Background copy 7")
		list1.putReference(ref1)
		desc1.putList(cID('null'), list1)
		app.executeAction(cID('Shw '), desc1, dialog_mode)

	# Select
	def step102(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Background copy 7")
		desc1.putReference(cID('null'), ref1)
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(250)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Set
	def step103(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		desc2 = ps.ActionDescriptor()
		desc2.putUnitDouble(cID('Opct'), cID('#Prc'), 50)
		desc1.putObject(cID('T   '), cID('Lyr '), desc2)
		app.executeAction(cID('setd'), desc1, dialog_mode)

	# Select
	def step104(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Background")
		desc1.putReference(cID('null'), ref1)
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(1)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Layer Via Copy
	def step105(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		app.executeAction(sID('copyToLayer'), ps.ActionDescriptor(), dialog_mode)

	# Move
	def step106(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		ref2 = ps.ActionReference()
		ref2.putIndex(cID('Lyr '), 11)
		desc1.putReference(cID('T   '), ref2)
		desc1.putBoolean(cID('Adjs'), False)
		desc1.putInteger(cID('Vrsn'), 5)
		list1 = ps.ActionList()
		list1.putInteger(261)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('move'), desc1, dialog_mode)

	# Wave
	def step107(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
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
	def step108(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putProperty(cID('Clr '), cID('Clrs'))
		desc1.putReference(cID('null'), ref1)
		app.executeAction(cID('Rset'), desc1, dialog_mode)

	# Filter Gallery
	def step109(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
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

	# Levels
	def step110(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		desc1.putBoolean(cID('Auto'), True)
		app.executeAction(cID('Lvls'), desc1, dialog_mode)

	# Levels
	def step111(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		desc1.putBoolean(cID('AuCo'), True)
		app.executeAction(cID('Lvls'), desc1, dialog_mode)

	# Set
	def step112(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		desc2 = ps.ActionDescriptor()
		desc2.putEnumerated(cID('Md  '), cID('BlnM'), cID('Mltp'))
		desc1.putObject(cID('T   '), cID('Lyr '), desc2)
		app.executeAction(cID('setd'), desc1, dialog_mode)

	# Set
	def step113(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		desc2 = ps.ActionDescriptor()
		desc2.putUnitDouble(cID('Opct'), cID('#Prc'), 50)
		desc1.putObject(cID('T   '), cID('Lyr '), desc2)
		app.executeAction(cID('setd'), desc1, dialog_mode)

	# Move
	def step114(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		ref2 = ps.ActionReference()
		ref2.putIndex(cID('Lyr '), 5)
		desc1.putReference(cID('T   '), ref2)
		desc1.putBoolean(cID('Adjs'), False)
		desc1.putInteger(cID('Vrsn'), 5)
		list1 = ps.ActionList()
		list1.putInteger(261)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('move'), desc1, dialog_mode)

	# Select
	def step115(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Background")
		desc1.putReference(cID('null'), ref1)
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(1)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Layer Via Copy
	def step116(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		app.executeAction(sID('copyToLayer'), ps.ActionDescriptor(), dialog_mode)

	# Move
	def step117(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		ref2 = ps.ActionReference()
		ref2.putIndex(cID('Lyr '), 12)
		desc1.putReference(cID('T   '), ref2)
		desc1.putBoolean(cID('Adjs'), False)
		desc1.putInteger(cID('Vrsn'), 5)
		list1 = ps.ActionList()
		list1.putInteger(263)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('move'), desc1, dialog_mode)

	# Reset
	def step118(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putProperty(cID('Clr '), cID('Clrs'))
		desc1.putReference(cID('null'), ref1)
		app.executeAction(cID('Rset'), desc1, dialog_mode)

	# Filter Gallery
	def step119(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		desc1.putEnumerated(cID('GEfk'), cID('GEft'), cID('Phtc'))
		desc1.putInteger(cID('Dtl '), 2)
		desc1.putInteger(cID('Drkn'), 5)
		app.executeAction(1195730531, desc1, dialog_mode)

	# Set
	def step120(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		desc2 = ps.ActionDescriptor()
		desc2.putEnumerated(cID('Md  '), cID('BlnM'), cID('Mltp'))
		desc1.putObject(cID('T   '), cID('Lyr '), desc2)
		app.executeAction(cID('setd'), desc1, dialog_mode)

	# Layer Via Copy
	def step121(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		app.executeAction(sID('copyToLayer'), ps.ActionDescriptor(), dialog_mode)

	# Transform
	def step122(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
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
		desc1.putUnitDouble(cID('Hght'), cID('#Prc'), 110.000002384186)
		desc1.putBoolean(cID('Lnkd'), True)
		desc1.putEnumerated(cID('Intr'), cID('Intp'), cID('Bcbc'))
		app.executeAction(cID('Trnf'), desc1, dialog_mode)

	# Select
	def step123(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Background copy 8")
		desc1.putReference(cID('null'), ref1)
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(263)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Transform
	def step124(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
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
		desc1.putUnitDouble(cID('Hght'), cID('#Prc'), 89.9999976158142)
		desc1.putBoolean(cID('Lnkd'), True)
		desc1.putEnumerated(cID('Intr'), cID('Intp'), cID('Bcbc'))
		app.executeAction(cID('Trnf'), desc1, dialog_mode)

	# Select
	def step125(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Background copy 9")
		desc1.putReference(cID('null'), ref1)
		desc1.putEnumerated(sID("selectionModifier"), sID("selectionModifierType"), sID("addToSelection"))
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(263)
		list1.putInteger(264)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Set
	def step126(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		desc2 = ps.ActionDescriptor()
		desc2.putUnitDouble(cID('Opct'), cID('#Prc'), 10)
		desc1.putObject(cID('T   '), cID('Lyr '), desc2)
		app.executeAction(cID('setd'), desc1, dialog_mode)

	# Move
	def step127(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		ref2 = ps.ActionReference()
		ref2.putIndex(cID('Lyr '), 8)
		desc1.putReference(cID('T   '), ref2)
		desc1.putBoolean(cID('Adjs'), False)
		desc1.putInteger(cID('Vrsn'), 5)
		list1 = ps.ActionList()
		list1.putInteger(263)
		list1.putInteger(264)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('move'), desc1, dialog_mode)

	# Select
	def step128(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Background copy 7")
		desc1.putReference(cID('null'), ref1)
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(250)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Select
	def step129(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Layer 2")
		desc1.putReference(cID('null'), ref1)
		desc1.putEnumerated(sID("selectionModifier"), sID("selectionModifierType"), sID("addToSelectionContinuous"))
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(250)
		list1.putInteger(240)
		list1.putInteger(242)
		list1.putInteger(261)
		list1.putInteger(244)
		list1.putInteger(246)
		list1.putInteger(263)
		list1.putInteger(264)
		list1.putInteger(258)
		list1.putInteger(255)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Set
	def step130(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		desc2 = ps.ActionDescriptor()
		desc2.putEnumerated(cID('Md  '), cID('BlnM'), sID("linearBurn"))
		desc1.putObject(cID('T   '), cID('Lyr '), desc2)
		app.executeAction(cID('setd'), desc1, dialog_mode)

	# Select
	def step131(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Color Fill 1")
		desc1.putReference(cID('null'), ref1)
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(238)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Make
	def step132(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putClass(cID('Lyr '))
		desc1.putReference(cID('null'), ref1)
		desc1.putInteger(cID('LyrI'), 268)
		app.executeAction(cID('Mk  '), desc1, dialog_mode)

	# Fill
	def step133(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		desc1.putEnumerated(cID('Usng'), cID('FlCn'), cID('Gry '))
		desc1.putUnitDouble(cID('Opct'), cID('#Prc'), 100)
		desc1.putEnumerated(cID('Md  '), cID('BlnM'), cID('Nrml'))
		app.executeAction(cID('Fl  '), desc1, dialog_mode)

	# Filter Gallery
	def step134(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		desc1.putEnumerated(cID('GEfk'), cID('GEft'), cID('Txtz'))
		desc1.putEnumerated(cID('TxtT'), cID('TxtT'), cID('TxSt'))
		desc1.putInteger(cID('Scln'), 200)
		desc1.putInteger(cID('Rlf '), 4)
		desc1.putEnumerated(cID('LghD'), cID('LghD'), cID('LDTp'))
		desc1.putBoolean(cID('InvT'), False)
		app.executeAction(1195730531, desc1, dialog_mode)

	# Set
	def step135(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		desc2 = ps.ActionDescriptor()
		desc2.putEnumerated(cID('Md  '), cID('BlnM'), cID('SftL'))
		desc1.putObject(cID('T   '), cID('Lyr '), desc2)
		app.executeAction(cID('setd'), desc1, dialog_mode)

	# Select
	def step136(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Color Fill 1")
		desc1.putReference(cID('null'), ref1)
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(238)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Set
	def step137(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(sID("contentLayer"), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		desc2 = ps.ActionDescriptor()
		desc3 = ps.ActionDescriptor()
		desc3.putDouble(cID('Rd  '), 166)
		desc3.putDouble(cID('Grn '), 166)
		desc3.putDouble(cID('Bl  '), 166)
		desc2.putObject(cID('Clr '), sID("RGBColor"), desc3)
		desc1.putObject(cID('T   '), sID("solidColorLayer"), desc2)
		app.executeAction(cID('setd'), desc1, dialog_mode)

	# Select
	def step138(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Layer 4")
		desc1.putReference(cID('null'), ref1)
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(268)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Make
	def step139(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putClass(cID('Lyr '))
		desc1.putReference(cID('null'), ref1)
		desc1.putInteger(cID('LyrI'), 269)
		app.executeAction(cID('Mk  '), desc1, dialog_mode)

	# Fill
	def step140(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		desc1.putEnumerated(cID('Usng'), cID('FlCn'), cID('FrgC'))
		desc1.putUnitDouble(cID('Opct'), cID('#Prc'), 100)
		desc1.putEnumerated(cID('Md  '), cID('BlnM'), cID('Nrml'))
		app.executeAction(cID('Fl  '), desc1, dialog_mode)

	# Add Noise
	def step141(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		desc1.putEnumerated(cID('Dstr'), cID('Dstr'), cID('Gsn '))
		desc1.putUnitDouble(cID('Nose'), cID('#Prc'), 25)
		desc1.putBoolean(cID('Mnch'), True)
		desc1.putInteger(cID('FlRs'), 1315132)
		app.executeAction(sID('addNoise'), desc1, dialog_mode)

	# Set
	def step142(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		desc2 = ps.ActionDescriptor()
		desc2.putEnumerated(cID('Md  '), cID('BlnM'), cID('Mltp'))
		desc1.putObject(cID('T   '), cID('Lyr '), desc2)
		app.executeAction(cID('setd'), desc1, dialog_mode)

	# Set
	def step143(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		desc2 = ps.ActionDescriptor()
		desc2.putEnumerated(cID('Md  '), cID('BlnM'), cID('Scrn'))
		desc1.putObject(cID('T   '), cID('Lyr '), desc2)
		app.executeAction(cID('setd'), desc1, dialog_mode)

	# Levels
	def step144(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
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
	def step145(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Background copy 4")
		desc1.putReference(cID('null'), ref1)
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(246)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Move
	def step146(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		ref2 = ps.ActionReference()
		ref2.putIndex(cID('Lyr '), 6)
		desc1.putReference(cID('T   '), ref2)
		desc1.putBoolean(cID('Adjs'), False)
		desc1.putInteger(cID('Vrsn'), 5)
		list1 = ps.ActionList()
		list1.putInteger(246)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('move'), desc1, dialog_mode)

	# Select
	def step147(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Background copy 3")
		desc1.putReference(cID('null'), ref1)
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(244)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Set
	def step148(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		desc2 = ps.ActionDescriptor()
		desc2.putUnitDouble(cID('Opct'), cID('#Prc'), 20)
		desc1.putObject(cID('T   '), cID('Lyr '), desc2)
		app.executeAction(cID('setd'), desc1, dialog_mode)

	# Select
	def step149(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Layer 3")
		desc1.putReference(cID('null'), ref1)
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(258)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Select
	def step150(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Layer 2")
		desc1.putReference(cID('null'), ref1)
		desc1.putEnumerated(sID("selectionModifier"), sID("selectionModifierType"), sID("addToSelection"))
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(258)
		list1.putInteger(255)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Set
	def step151(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		desc2 = ps.ActionDescriptor()
		desc2.putUnitDouble(cID('Opct'), cID('#Prc'), 40)
		desc1.putObject(cID('T   '), cID('Lyr '), desc2)
		app.executeAction(cID('setd'), desc1, dialog_mode)

	# Select
	def step152(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Background copy 5")
		desc1.putReference(cID('null'), ref1)
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(252)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Reset
	def step153(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putProperty(cID('Clr '), cID('Clrs'))
		desc1.putReference(cID('null'), ref1)
		app.executeAction(cID('Rset'), desc1, dialog_mode)

	# Make
	def step154(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
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
	def step155(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('AdjL'), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		desc1.putClass(cID('T   '), cID('GdMp'))
		app.executeAction(cID('setd'), desc1, dialog_mode)

	# Set
	def step156(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		desc2 = ps.ActionDescriptor()
		desc2.putEnumerated(cID('Md  '), cID('BlnM'), cID('SftL'))
		desc1.putObject(cID('T   '), cID('Lyr '), desc2)
		app.executeAction(cID('setd'), desc1, dialog_mode)

	# Set
	def step157(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		desc2 = ps.ActionDescriptor()
		desc2.putUnitDouble(cID('Opct'), cID('#Prc'), 20)
		desc1.putObject(cID('T   '), cID('Lyr '), desc2)
		app.executeAction(cID('setd'), desc1, dialog_mode)

	# Make
	def step158(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
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

	# Set
	def step159(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
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
	def step160(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Background copy 6")
		desc1.putReference(cID('null'), ref1)
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(112)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Set
	def step161(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		desc2 = ps.ActionDescriptor()
		desc2.putUnitDouble(cID('Opct'), cID('#Prc'), 40)
		desc1.putObject(cID('T   '), cID('Lyr '), desc2)
		app.executeAction(cID('setd'), desc1, dialog_mode)

	# Select
	def step162(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Background")
		desc1.putReference(cID('null'), ref1)
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(1)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Layer Via Copy
	def step163(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		app.executeAction(sID('copyToLayer'), ps.ActionDescriptor(), dialog_mode)

	# Move
	def step164(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		ref2 = ps.ActionReference()
		ref2.putIndex(cID('Lyr '), 18)
		desc1.putReference(cID('T   '), ref2)
		desc1.putBoolean(cID('Adjs'), False)
		desc1.putInteger(cID('Vrsn'), 5)
		list1 = ps.ActionList()
		list1.putInteger(121)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('move'), desc1, dialog_mode)

	# Reset
	def step165(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putProperty(cID('Clr '), cID('Clrs'))
		desc1.putReference(cID('null'), ref1)
		app.executeAction(cID('Rset'), desc1, dialog_mode)

	# Filter Gallery
	def step166(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		desc1.putEnumerated(cID('GEfk'), cID('GEft'), cID('GraP'))
		desc1.putInteger(cID('StrL'), 15)
		desc1.putInteger(cID('LgDr'), 50)
		desc1.putEnumerated(cID('SDir'), cID('StrD'), cID('SDRD'))
		app.executeAction(1195730531, desc1, dialog_mode)

	# Set
	def step167(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		desc2 = ps.ActionDescriptor()
		desc2.putEnumerated(cID('Md  '), cID('BlnM'), cID('Ovrl'))
		desc1.putObject(cID('T   '), cID('Lyr '), desc2)
		app.executeAction(cID('setd'), desc1, dialog_mode)

	# Set
	def step168(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		desc2 = ps.ActionDescriptor()
		desc2.putUnitDouble(cID('Opct'), cID('#Prc'), 30)
		desc1.putObject(cID('T   '), cID('Lyr '), desc2)
		app.executeAction(cID('setd'), desc1, dialog_mode)

	# Move
	def step169(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		ref2 = ps.ActionReference()
		ref2.putIndex(cID('Lyr '), 5)
		desc1.putReference(cID('T   '), ref2)
		desc1.putBoolean(cID('Adjs'), False)
		desc1.putInteger(cID('Vrsn'), 5)
		list1 = ps.ActionList()
		list1.putInteger(121)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('move'), desc1, dialog_mode)

	# Select
	def step170(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Background")
		desc1.putReference(cID('null'), ref1)
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(1)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Layer Via Copy
	def step171(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		app.executeAction(sID('copyToLayer'), ps.ActionDescriptor(), dialog_mode)

	# Move
	def step172(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		ref2 = ps.ActionReference()
		ref2.putIndex(cID('Lyr '), 19)
		desc1.putReference(cID('T   '), ref2)
		desc1.putBoolean(cID('Adjs'), False)
		desc1.putInteger(cID('Vrsn'), 5)
		list1 = ps.ActionList()
		list1.putInteger(127)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('move'), desc1, dialog_mode)

	# Set
	def step173(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		desc2 = ps.ActionDescriptor()
		desc2.putEnumerated(cID('Md  '), cID('BlnM'), cID('Clr '))
		desc1.putObject(cID('T   '), cID('Lyr '), desc2)
		app.executeAction(cID('setd'), desc1, dialog_mode)

	# Make
	def step174(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
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
	def step175(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		app.executeAction(sID('groupEvent'), desc1, dialog_mode)

	# Hide
	def step176(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		list1 = ps.ActionList()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Background copy 11")
		list1.putReference(ref1)
		desc1.putList(cID('null'), list1)
		app.executeAction(cID('Hd  '), desc1, dialog_mode)

	# Select
	def step177(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Background copy 11")
		desc1.putReference(cID('null'), ref1)
		desc1.putEnumerated(sID("selectionModifier"), sID("selectionModifierType"), sID("addToSelection"))
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(127)
		list1.putInteger(128)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Move
	def step178(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		ref2 = ps.ActionReference()
		ref2.putIndex(cID('Lyr '), 16)
		desc1.putReference(cID('T   '), ref2)
		desc1.putBoolean(cID('Adjs'), False)
		desc1.putInteger(cID('Vrsn'), 5)
		list1 = ps.ActionList()
		list1.putInteger(127)
		list1.putInteger(128)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('move'), desc1, dialog_mode)

	# Select
	def step179(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Levels 1")
		desc1.putReference(cID('null'), ref1)
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(119)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Make
	def step180(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
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
	def step181(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		desc1.putBoolean(cID('Dplc'), True)
		app.executeAction(sID('mergeVisible'), desc1, dialog_mode)

	# Desaturate
	def step182(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		app.executeAction(cID('Dstt'), ps.ActionDescriptor(), dialog_mode)

	# High Pass
	def step183(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		desc1.putUnitDouble(cID('Rds '), cID('#Pxl'), 1)
		app.executeAction(sID('highPass'), desc1, dialog_mode)

	# Set
	def step184(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		desc2 = ps.ActionDescriptor()
		desc2.putEnumerated(cID('Md  '), cID('BlnM'), sID("vividLight"))
		desc1.putObject(cID('T   '), cID('Lyr '), desc2)
		app.executeAction(cID('setd'), desc1, dialog_mode)

	# Select
	def step185(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
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
	def step186(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
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
	def step187(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
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
	def step188(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		desc1.putClass(cID('Nw  '), cID('Chnl'))
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Chnl'), cID('Chnl'), cID('Msk '))
		desc1.putReference(cID('At  '), ref1)
		desc1.putEnumerated(cID('Usng'), cID('UsrM'), cID('RvlA'))
		app.executeAction(cID('Mk  '), desc1, dialog_mode)

	# Set
	def step189(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		desc2 = ps.ActionDescriptor()
		desc2.putBoolean(cID('Usrs'), False)
		desc1.putObject(cID('T   '), cID('Lyr '), desc2)
		app.executeAction(cID('setd'), desc1, dialog_mode)

	# Select
	def step190(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
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
	def step191(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		list1 = ps.ActionList()
		list1.putInteger(139)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('Dlt '), desc1, dialog_mode)

	# Select
	def step192(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Color Fill 1")
		desc1.putReference(cID('null'), ref1)
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(140)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Set
	def step193(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		desc2 = ps.ActionDescriptor()
		desc2.putString(cID('Nm  '), "Background Color")
		desc1.putObject(cID('T   '), cID('Lyr '), desc2)
		app.executeAction(cID('setd'), desc1, dialog_mode)

	# Select
	def step194(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Layer 4")
		desc1.putReference(cID('null'), ref1)
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(166)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Set
	def step195(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		desc2 = ps.ActionDescriptor()
		desc2.putString(cID('Nm  '), "Paper")
		desc1.putObject(cID('T   '), cID('Lyr '), desc2)
		app.executeAction(cID('setd'), desc1, dialog_mode)

	# Select
	def step196(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Layer 5")
		desc1.putReference(cID('null'), ref1)
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(167)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Set
	def step197(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		desc2 = ps.ActionDescriptor()
		desc2.putString(cID('Nm  '), "Noise")
		desc1.putObject(cID('T   '), cID('Lyr '), desc2)
		app.executeAction(cID('setd'), desc1, dialog_mode)

	# Select
	def step198(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Paper")
		desc1.putReference(cID('null'), ref1)
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(166)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Select
	def step199(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Noise")
		desc1.putReference(cID('null'), ref1)
		desc1.putEnumerated(sID("selectionModifier"), sID("selectionModifierType"), sID("addToSelection"))
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(166)
		list1.putInteger(167)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Make
	def step200(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putClass(sID("layerSection"))
		desc1.putReference(cID('null'), ref1)
		ref2 = ps.ActionReference()
		ref2.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('From'), ref2)
		desc2 = ps.ActionDescriptor()
		desc2.putString(cID('Nm  '), "Textures")
		desc1.putObject(cID('Usng'), sID("layerSection"), desc2)
		desc1.putInteger(sID("layerSectionStart"), 179)
		desc1.putInteger(sID("layerSectionEnd"), 180)
		desc1.putString(cID('Nm  '), "Textures")
		app.executeAction(cID('Mk  '), desc1, dialog_mode)

	# Make
	def step201(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		desc1.putClass(cID('Nw  '), cID('Chnl'))
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Chnl'), cID('Chnl'), cID('Msk '))
		desc1.putReference(cID('At  '), ref1)
		desc1.putEnumerated(cID('Usng'), cID('UsrM'), cID('RvlA'))
		app.executeAction(cID('Mk  '), desc1, dialog_mode)

	# Set
	def step202(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		desc2 = ps.ActionDescriptor()
		desc2.putBoolean(cID('Usrs'), False)
		desc1.putObject(cID('T   '), cID('Lyr '), desc2)
		app.executeAction(cID('setd'), desc1, dialog_mode)

	# Select
	def step203(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Paper")
		desc1.putReference(cID('null'), ref1)
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(166)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Make
	def step204(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		desc1.putClass(cID('Nw  '), cID('Chnl'))
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Chnl'), cID('Chnl'), cID('Msk '))
		desc1.putReference(cID('At  '), ref1)
		desc1.putEnumerated(cID('Usng'), cID('UsrM'), cID('RvlA'))
		app.executeAction(cID('Mk  '), desc1, dialog_mode)

	# Select
	def step205(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Noise")
		desc1.putReference(cID('null'), ref1)
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(167)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Make
	def step206(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		desc1.putClass(cID('Nw  '), cID('Chnl'))
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Chnl'), cID('Chnl'), cID('Msk '))
		desc1.putReference(cID('At  '), ref1)
		desc1.putEnumerated(cID('Usng'), cID('UsrM'), cID('RvlA'))
		app.executeAction(cID('Mk  '), desc1, dialog_mode)

	# Select
	def step207(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Background copy 7")
		desc1.putReference(cID('null'), ref1)
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(152)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Set
	def step208(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		desc2 = ps.ActionDescriptor()
		desc2.putString(cID('Nm  '), "Shading_2")
		desc1.putObject(cID('T   '), cID('Lyr '), desc2)
		app.executeAction(cID('setd'), desc1, dialog_mode)

	# Select
	def step209(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Background copy 10")
		desc1.putReference(cID('null'), ref1)
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(171)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Set
	def step210(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		desc2 = ps.ActionDescriptor()
		desc2.putString(cID('Nm  '), "Shading_1")
		desc1.putObject(cID('T   '), cID('Lyr '), desc2)
		app.executeAction(cID('setd'), desc1, dialog_mode)

	# Make
	def step211(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		desc1.putClass(cID('Nw  '), cID('Chnl'))
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Chnl'), cID('Chnl'), cID('Msk '))
		desc1.putReference(cID('At  '), ref1)
		desc1.putEnumerated(cID('Usng'), cID('UsrM'), cID('RvlA'))
		app.executeAction(cID('Mk  '), desc1, dialog_mode)

	# Select
	def step212(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Shading_2")
		desc1.putReference(cID('null'), ref1)
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(152)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Make
	def step213(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		desc1.putClass(cID('Nw  '), cID('Chnl'))
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Chnl'), cID('Chnl'), cID('Msk '))
		desc1.putReference(cID('At  '), ref1)
		desc1.putEnumerated(cID('Usng'), cID('UsrM'), cID('RvlA'))
		app.executeAction(cID('Mk  '), desc1, dialog_mode)

	# Select
	def step214(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Shading_1")
		desc1.putReference(cID('null'), ref1)
		desc1.putEnumerated(sID("selectionModifier"), sID("selectionModifierType"), sID("addToSelection"))
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(152)
		list1.putInteger(171)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Make
	def step215(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putClass(sID("layerSection"))
		desc1.putReference(cID('null'), ref1)
		ref2 = ps.ActionReference()
		ref2.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('From'), ref2)
		desc2 = ps.ActionDescriptor()
		desc2.putString(cID('Nm  '), "Shading")
		desc1.putObject(cID('Usng'), sID("layerSection"), desc2)
		desc1.putInteger(sID("layerSectionStart"), 181)
		desc1.putInteger(sID("layerSectionEnd"), 182)
		desc1.putString(cID('Nm  '), "Shading")
		app.executeAction(cID('Mk  '), desc1, dialog_mode)

	# Make
	def step216(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		desc1.putClass(cID('Nw  '), cID('Chnl'))
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Chnl'), cID('Chnl'), cID('Msk '))
		desc1.putReference(cID('At  '), ref1)
		desc1.putEnumerated(cID('Usng'), cID('UsrM'), cID('RvlA'))
		app.executeAction(cID('Mk  '), desc1, dialog_mode)

	# Set
	def step217(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		desc2 = ps.ActionDescriptor()
		desc2.putBoolean(cID('Usrs'), False)
		desc1.putObject(cID('T   '), cID('Lyr '), desc2)
		app.executeAction(cID('setd'), desc1, dialog_mode)

	# Select
	def step218(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Background copy")
		desc1.putReference(cID('null'), ref1)
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(142)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Set
	def step219(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		desc2 = ps.ActionDescriptor()
		desc2.putString(cID('Nm  '), "Basic Sketch")
		desc1.putObject(cID('T   '), cID('Lyr '), desc2)
		app.executeAction(cID('setd'), desc1, dialog_mode)

	# Make
	def step220(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		desc1.putClass(cID('Nw  '), cID('Chnl'))
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Chnl'), cID('Chnl'), cID('Msk '))
		desc1.putReference(cID('At  '), ref1)
		desc1.putEnumerated(cID('Usng'), cID('UsrM'), cID('RvlA'))
		app.executeAction(cID('Mk  '), desc1, dialog_mode)

	# Select
	def step221(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Background copy 4")
		desc1.putReference(cID('null'), ref1)
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(148)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Set
	def step222(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		desc2 = ps.ActionDescriptor()
		desc2.putString(cID('Nm  '), "Smooth Sketch")
		desc1.putObject(cID('T   '), cID('Lyr '), desc2)
		app.executeAction(cID('setd'), desc1, dialog_mode)

	# Make
	def step223(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		desc1.putClass(cID('Nw  '), cID('Chnl'))
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Chnl'), cID('Chnl'), cID('Msk '))
		desc1.putReference(cID('At  '), ref1)
		desc1.putEnumerated(cID('Usng'), cID('UsrM'), cID('RvlA'))
		app.executeAction(cID('Mk  '), desc1, dialog_mode)

	# Select
	def step224(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Background copy 2")
		desc1.putReference(cID('null'), ref1)
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(144)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Set
	def step225(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		desc2 = ps.ActionDescriptor()
		desc2.putString(cID('Nm  '), "Outline Sketch")
		desc1.putObject(cID('T   '), cID('Lyr '), desc2)
		app.executeAction(cID('setd'), desc1, dialog_mode)

	# Make
	def step226(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		desc1.putClass(cID('Nw  '), cID('Chnl'))
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Chnl'), cID('Chnl'), cID('Msk '))
		desc1.putReference(cID('At  '), ref1)
		desc1.putEnumerated(cID('Usng'), cID('UsrM'), cID('RvlA'))
		app.executeAction(cID('Mk  '), desc1, dialog_mode)

	# Select
	def step227(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Background copy 6")
		desc1.putReference(cID('null'), ref1)
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(162)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Set
	def step228(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		desc2 = ps.ActionDescriptor()
		desc2.putUnitDouble(cID('Opct'), cID('#Prc'), 20)
		desc1.putObject(cID('T   '), cID('Lyr '), desc2)
		app.executeAction(cID('setd'), desc1, dialog_mode)

	# Select
	def step229(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Background copy 9")
		desc1.putReference(cID('null'), ref1)
		desc1.putEnumerated(sID("selectionModifier"), sID("selectionModifierType"), sID("addToSelectionContinuous"))
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(162)
		list1.putInteger(146)
		list1.putInteger(164)
		list1.putInteger(165)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Make
	def step230(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putClass(sID("layerSection"))
		desc1.putReference(cID('null'), ref1)
		ref2 = ps.ActionReference()
		ref2.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('From'), ref2)
		desc2 = ps.ActionDescriptor()
		desc2.putString(cID('Nm  '), "Draft Sketch")
		desc1.putObject(cID('Usng'), sID("layerSection"), desc2)
		desc1.putInteger(sID("layerSectionStart"), 183)
		desc1.putInteger(sID("layerSectionEnd"), 184)
		desc1.putString(cID('Nm  '), "Draft Sketch")
		app.executeAction(cID('Mk  '), desc1, dialog_mode)

	# Make
	def step231(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		desc1.putClass(cID('Nw  '), cID('Chnl'))
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Chnl'), cID('Chnl'), cID('Msk '))
		desc1.putReference(cID('At  '), ref1)
		desc1.putEnumerated(cID('Usng'), cID('UsrM'), cID('RvlA'))
		app.executeAction(cID('Mk  '), desc1, dialog_mode)

	# Set
	def step232(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		desc2 = ps.ActionDescriptor()
		desc2.putBoolean(cID('Usrs'), False)
		desc1.putObject(cID('T   '), cID('Lyr '), desc2)
		app.executeAction(cID('setd'), desc1, dialog_mode)

	# Select
	def step233(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Background copy 9")
		desc1.putReference(cID('null'), ref1)
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(165)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Set
	def step234(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		desc2 = ps.ActionDescriptor()
		desc2.putString(cID('Nm  '), "DS_1")
		desc1.putObject(cID('T   '), cID('Lyr '), desc2)
		app.executeAction(cID('setd'), desc1, dialog_mode)

	# Select
	def step235(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Background copy 8")
		desc1.putReference(cID('null'), ref1)
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(164)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Set
	def step236(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		desc2 = ps.ActionDescriptor()
		desc2.putString(cID('Nm  '), "DS_2")
		desc1.putObject(cID('T   '), cID('Lyr '), desc2)
		app.executeAction(cID('setd'), desc1, dialog_mode)

	# Select
	def step237(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Background copy 3")
		desc1.putReference(cID('null'), ref1)
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(146)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Set
	def step238(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		desc2 = ps.ActionDescriptor()
		desc2.putString(cID('Nm  '), "DS_3")
		desc1.putObject(cID('T   '), cID('Lyr '), desc2)
		app.executeAction(cID('setd'), desc1, dialog_mode)

	# Select
	def step239(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Background copy 6")
		desc1.putReference(cID('null'), ref1)
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(162)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Set
	def step240(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		desc2 = ps.ActionDescriptor()
		desc2.putString(cID('Nm  '), "DS_4")
		desc1.putObject(cID('T   '), cID('Lyr '), desc2)
		app.executeAction(cID('setd'), desc1, dialog_mode)

	# Select
	def step241(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "DS_1")
		desc1.putReference(cID('null'), ref1)
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(165)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Make
	def step242(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		desc1.putClass(cID('Nw  '), cID('Chnl'))
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Chnl'), cID('Chnl'), cID('Msk '))
		desc1.putReference(cID('At  '), ref1)
		desc1.putEnumerated(cID('Usng'), cID('UsrM'), cID('RvlA'))
		app.executeAction(cID('Mk  '), desc1, dialog_mode)

	# Select
	def step243(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "DS_2")
		desc1.putReference(cID('null'), ref1)
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(164)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Make
	def step244(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		desc1.putClass(cID('Nw  '), cID('Chnl'))
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Chnl'), cID('Chnl'), cID('Msk '))
		desc1.putReference(cID('At  '), ref1)
		desc1.putEnumerated(cID('Usng'), cID('UsrM'), cID('RvlA'))
		app.executeAction(cID('Mk  '), desc1, dialog_mode)

	# Select
	def step245(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "DS_3")
		desc1.putReference(cID('null'), ref1)
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(146)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Make
	def step246(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		desc1.putClass(cID('Nw  '), cID('Chnl'))
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Chnl'), cID('Chnl'), cID('Msk '))
		desc1.putReference(cID('At  '), ref1)
		desc1.putEnumerated(cID('Usng'), cID('UsrM'), cID('RvlA'))
		app.executeAction(cID('Mk  '), desc1, dialog_mode)

	# Select
	def step247(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "DS_4")
		desc1.putReference(cID('null'), ref1)
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(162)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Make
	def step248(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		desc1.putClass(cID('Nw  '), cID('Chnl'))
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Chnl'), cID('Chnl'), cID('Msk '))
		desc1.putReference(cID('At  '), ref1)
		desc1.putEnumerated(cID('Usng'), cID('UsrM'), cID('RvlA'))
		app.executeAction(cID('Mk  '), desc1, dialog_mode)

	# Select
	def step249(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Draft Sketch")
		desc1.putReference(cID('null'), ref1)
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(183)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Select
	def step250(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Layer 2")
		desc1.putReference(cID('null'), ref1)
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(157)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Select
	def step251(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Layer 3")
		desc1.putReference(cID('null'), ref1)
		desc1.putEnumerated(sID("selectionModifier"), sID("selectionModifierType"), sID("addToSelection"))
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(160)
		list1.putInteger(157)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Make
	def step252(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putClass(sID("layerSection"))
		desc1.putReference(cID('null'), ref1)
		ref2 = ps.ActionReference()
		ref2.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('From'), ref2)
		desc2 = ps.ActionDescriptor()
		desc2.putString(cID('Nm  '), "Rough Sketch")
		desc1.putObject(cID('Usng'), sID("layerSection"), desc2)
		desc1.putInteger(sID("layerSectionStart"), 185)
		desc1.putInteger(sID("layerSectionEnd"), 186)
		desc1.putString(cID('Nm  '), "Rough Sketch")
		app.executeAction(cID('Mk  '), desc1, dialog_mode)

	# Make
	def step253(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		desc1.putClass(cID('Nw  '), cID('Chnl'))
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Chnl'), cID('Chnl'), cID('Msk '))
		desc1.putReference(cID('At  '), ref1)
		desc1.putEnumerated(cID('Usng'), cID('UsrM'), cID('RvlA'))
		app.executeAction(cID('Mk  '), desc1, dialog_mode)

	# Set
	def step254(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		desc2 = ps.ActionDescriptor()
		desc2.putBoolean(cID('Usrs'), False)
		desc1.putObject(cID('T   '), cID('Lyr '), desc2)
		app.executeAction(cID('setd'), desc1, dialog_mode)

	# Select
	def step255(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Layer 2")
		desc1.putReference(cID('null'), ref1)
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(157)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Set
	def step256(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		desc2 = ps.ActionDescriptor()
		desc2.putString(cID('Nm  '), "RS_1")
		desc1.putObject(cID('T   '), cID('Lyr '), desc2)
		app.executeAction(cID('setd'), desc1, dialog_mode)

	# Select
	def step257(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Layer 3")
		desc1.putReference(cID('null'), ref1)
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(160)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Set
	def step258(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		desc2 = ps.ActionDescriptor()
		desc2.putString(cID('Nm  '), "RS_2")
		desc1.putObject(cID('T   '), cID('Lyr '), desc2)
		app.executeAction(cID('setd'), desc1, dialog_mode)

	# Make
	def step259(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		desc1.putClass(cID('Nw  '), cID('Chnl'))
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Chnl'), cID('Chnl'), cID('Msk '))
		desc1.putReference(cID('At  '), ref1)
		desc1.putEnumerated(cID('Usng'), cID('UsrM'), cID('RvlA'))
		app.executeAction(cID('Mk  '), desc1, dialog_mode)

	# Select
	def step260(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "RS_1")
		desc1.putReference(cID('null'), ref1)
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(157)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Make
	def step261(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		desc1.putClass(cID('Nw  '), cID('Chnl'))
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Chnl'), cID('Chnl'), cID('Msk '))
		desc1.putReference(cID('At  '), ref1)
		desc1.putEnumerated(cID('Usng'), cID('UsrM'), cID('RvlA'))
		app.executeAction(cID('Mk  '), desc1, dialog_mode)

	# Select
	def step262(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Background copy 5")
		desc1.putReference(cID('null'), ref1)
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(154)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Set
	def step263(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		desc2 = ps.ActionDescriptor()
		desc2.putString(cID('Nm  '), "Reveal Details")
		desc1.putObject(cID('T   '), cID('Lyr '), desc2)
		app.executeAction(cID('setd'), desc1, dialog_mode)

	# Make
	def step264(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		desc1.putClass(cID('Nw  '), cID('Chnl'))
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Chnl'), cID('Chnl'), cID('Msk '))
		desc1.putReference(cID('At  '), ref1)
		desc1.putEnumerated(cID('Usng'), cID('UsrM'), cID('RvlA'))
		app.executeAction(cID('Mk  '), desc1, dialog_mode)

	# Select
	def step265(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Shading_2")
		desc1.putReference(cID('null'), ref1)
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(152)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Set
	def step266(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		desc2 = ps.ActionDescriptor()
		desc2.putUnitDouble(cID('Opct'), cID('#Prc'), 30)
		desc1.putObject(cID('T   '), cID('Lyr '), desc2)
		app.executeAction(cID('setd'), desc1, dialog_mode)

	# Select
	def step267(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Background copy 11")
		desc1.putReference(cID('null'), ref1)
		desc1.putBoolean(cID('MkVs'), True)
		list1 = ps.ActionList()
		list1.putInteger(173)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Set
	def step268(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		desc2 = ps.ActionDescriptor()
		desc2.putString(cID('Nm  '), "Colorize Sketch")
		desc1.putObject(cID('T   '), cID('Lyr '), desc2)
		app.executeAction(cID('setd'), desc1, dialog_mode)

	# Make HIDE THIS
	def step269(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		desc1.putClass(cID('Nw  '), cID('Chnl'))
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Chnl'), cID('Chnl'), cID('Msk '))
		desc1.putReference(cID('At  '), ref1)
		desc1.putEnumerated(cID('Usng'), cID('UsrM'), cID('RvlA'))
		app.executeAction(cID('Mk  '), desc1, dialog_mode)

	# Select HIDE THIS
	def step270(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Hue/Saturation 1")
		desc1.putReference(cID('null'), ref1)
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(174)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Set HIDE THIS
	def step271(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		desc2 = ps.ActionDescriptor()
		desc2.putString(cID('Nm  '), "Select Color")
		desc1.putObject(cID('T   '), cID('Lyr '), desc2)
		app.executeAction(cID('setd'), desc1, dialog_mode)

	# Select
	def step272(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Gradient Map 1")
		desc1.putReference(cID('null'), ref1)
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(168)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Select
	def step273(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Chnl'), cID('Chnl'), sID("RGB"))
		desc1.putReference(cID('null'), ref1)
		desc1.putBoolean(cID('MkVs'), False)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Set
	def step274(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		desc2 = ps.ActionDescriptor()
		desc2.putString(cID('Nm  '), "Overall Contrast")
		desc1.putObject(cID('T   '), cID('Lyr '), desc2)
		app.executeAction(cID('setd'), desc1, dialog_mode)

	# Select
	def step275(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Levels 1")
		desc1.putReference(cID('null'), ref1)
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(169)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Set
	def step276(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		desc2 = ps.ActionDescriptor()
		desc2.putString(cID('Nm  '), "Overall Brightness")
		desc1.putObject(cID('T   '), cID('Lyr '), desc2)
		app.executeAction(cID('setd'), desc1, dialog_mode)

	# Select
	def step277(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Hue/Saturation 1")
		desc1.putReference(cID('null'), ref1)
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(175)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Set
	def step278(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		desc2 = ps.ActionDescriptor()
		desc2.putString(cID('Nm  '), "Overall Saturation")
		desc1.putObject(cID('T   '), cID('Lyr '), desc2)
		app.executeAction(cID('setd'), desc1, dialog_mode)

	# Set
	def step279(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('AdjL'), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		desc2 = ps.ActionDescriptor()
		desc2.putEnumerated(sID("presetKind"), sID("presetKindType"), sID("presetKindCustom"))
		list1 = ps.ActionList()
		desc3 = ps.ActionDescriptor()
		desc3.putInteger(cID('H   '), 0)
		desc3.putInteger(cID('Strt'), 10)
		desc3.putInteger(cID('Lght'), 0)
		list1.putObject(cID('Hst2'), desc3)
		desc2.putList(cID('Adjs'), list1)
		desc1.putObject(cID('T   '), cID('HStr'), desc2)
		app.executeAction(cID('setd'), desc1, dialog_mode)

	# Select
	def step280(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Layer 6")
		desc1.putReference(cID('null'), ref1)
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(176)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Delete
	def step281(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		list1 = ps.ActionList()
		list1.putInteger(176)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('Dlt '), desc1, dialog_mode)

	# Select
	def step282(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Noise")
		desc1.putReference(cID('null'), ref1)
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(167)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Set
	def step283(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		desc2 = ps.ActionDescriptor()
		desc2.putUnitDouble(cID('Opct'), cID('#Prc'), 60)
		desc1.putObject(cID('T   '), cID('Lyr '), desc2)
		app.executeAction(cID('setd'), desc1, dialog_mode)

	# Select
	def step284(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Overall Saturation")
		desc1.putReference(cID('null'), ref1)
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(175)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Merge Visible
	def step285(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		desc1.putBoolean(cID('Dplc'), True)
		app.executeAction(sID('mergeVisible'), desc1, dialog_mode)

	# Desaturate
	def step286(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		app.executeAction(cID('Dstt'), ps.ActionDescriptor(), dialog_mode)

	# High Pass
	def step287(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		desc1.putUnitDouble(cID('Rds '), cID('#Pxl'), 1)
		app.executeAction(sID('highPass'), desc1, dialog_mode)

	# Set
	def step288(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		desc2 = ps.ActionDescriptor()
		desc2.putEnumerated(cID('Md  '), cID('BlnM'), sID("vividLight"))
		desc1.putObject(cID('T   '), cID('Lyr '), desc2)
		app.executeAction(cID('setd'), desc1, dialog_mode)

	# Set
	def step289(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		desc2 = ps.ActionDescriptor()
		desc2.putString(cID('Nm  '), "Overall Sharpening")
		desc1.putObject(cID('T   '), cID('Lyr '), desc2)
		app.executeAction(cID('setd'), desc1, dialog_mode)

	# Make
	def step290(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		desc1.putClass(cID('Nw  '), cID('Chnl'))
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Chnl'), cID('Chnl'), cID('Msk '))
		desc1.putReference(cID('At  '), ref1)
		desc1.putEnumerated(cID('Usng'), cID('UsrM'), cID('RvlA'))
		app.executeAction(cID('Mk  '), desc1, dialog_mode)

	# Select
	def step291(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Select Color")
		desc1.putReference(cID('null'), ref1)
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(95)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Layer Via Copy
	def step292(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		app.executeAction(sID('copyToLayer'), ps.ActionDescriptor(), dialog_mode)

	# Layer Via Copy
	def step293(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		app.executeAction(sID('copyToLayer'), ps.ActionDescriptor(), dialog_mode)

	# Layer Via Copy
	def step294(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		app.executeAction(sID('copyToLayer'), ps.ActionDescriptor(), dialog_mode)

	# Layer Via Copy
	def step295(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		app.executeAction(sID('copyToLayer'), ps.ActionDescriptor(), dialog_mode)

	# Layer Via Copy
	def step296(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		app.executeAction(sID('copyToLayer'), ps.ActionDescriptor(), dialog_mode)

	# Select
	def step297(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Select Color copy")
		desc1.putReference(cID('null'), ref1)
		desc1.putEnumerated(sID("selectionModifier"), sID("selectionModifierType"), sID("addToSelectionContinuous"))
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(109)
		list1.putInteger(110)
		list1.putInteger(111)
		list1.putInteger(112)
		list1.putInteger(113)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Create Clipping Mask
	def step298(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		app.executeAction(sID('groupEvent'), desc1, dialog_mode)

	# Select
	def step299(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Select Color")
		desc1.putReference(cID('null'), ref1)
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(95)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Select
	def step300(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Chnl'), cID('Chnl'), sID("RGB"))
		desc1.putReference(cID('null'), ref1)
		desc1.putBoolean(cID('MkVs'), False)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Set
	def step301(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('AdjL'), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		desc2 = ps.ActionDescriptor()
		desc2.putEnumerated(sID("presetKind"), sID("presetKindType"), sID("presetKindCustom"))
		list1 = ps.ActionList()
		desc3 = ps.ActionDescriptor()
		desc3.putInteger(cID('LclR'), 2)
		desc3.putInteger(cID('BgnR'), 15)
		desc3.putInteger(cID('BgnS'), 45)
		desc3.putInteger(cID('EndS'), 75)
		desc3.putInteger(cID('EndR'), 105)
		desc3.putInteger(cID('H   '), 0)
		desc3.putInteger(cID('Strt'), -100)
		desc3.putInteger(cID('Lght'), 0)
		list1.putObject(cID('Hst2'), desc3)
		desc4 = ps.ActionDescriptor()
		desc4.putInteger(cID('LclR'), 3)
		desc4.putInteger(cID('BgnR'), 75)
		desc4.putInteger(cID('BgnS'), 105)
		desc4.putInteger(cID('EndS'), 135)
		desc4.putInteger(cID('EndR'), 165)
		desc4.putInteger(cID('H   '), 0)
		desc4.putInteger(cID('Strt'), -100)
		desc4.putInteger(cID('Lght'), 0)
		list1.putObject(cID('Hst2'), desc4)
		desc5 = ps.ActionDescriptor()
		desc5.putInteger(cID('LclR'), 4)
		desc5.putInteger(cID('BgnR'), 135)
		desc5.putInteger(cID('BgnS'), 165)
		desc5.putInteger(cID('EndS'), 195)
		desc5.putInteger(cID('EndR'), 225)
		desc5.putInteger(cID('H   '), 0)
		desc5.putInteger(cID('Strt'), -100)
		desc5.putInteger(cID('Lght'), 0)
		list1.putObject(cID('Hst2'), desc5)
		desc6 = ps.ActionDescriptor()
		desc6.putInteger(cID('LclR'), 5)
		desc6.putInteger(cID('BgnR'), 195)
		desc6.putInteger(cID('BgnS'), 225)
		desc6.putInteger(cID('EndS'), 255)
		desc6.putInteger(cID('EndR'), 285)
		desc6.putInteger(cID('H   '), 0)
		desc6.putInteger(cID('Strt'), -100)
		desc6.putInteger(cID('Lght'), 0)
		list1.putObject(cID('Hst2'), desc6)
		desc7 = ps.ActionDescriptor()
		desc7.putInteger(cID('LclR'), 6)
		desc7.putInteger(cID('BgnR'), 255)
		desc7.putInteger(cID('BgnS'), 285)
		desc7.putInteger(cID('EndS'), 315)
		desc7.putInteger(cID('EndR'), 345)
		desc7.putInteger(cID('H   '), 0)
		desc7.putInteger(cID('Strt'), -100)
		desc7.putInteger(cID('Lght'), 0)
		list1.putObject(cID('Hst2'), desc7)
		desc2.putList(cID('Adjs'), list1)
		desc1.putObject(cID('T   '), cID('HStr'), desc2)
		app.executeAction(cID('setd'), desc1, dialog_mode)

	# Set
	def step302(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		desc2 = ps.ActionDescriptor()
		desc2.putString(cID('Nm  '), "Reds Only")
		desc1.putObject(cID('T   '), cID('Lyr '), desc2)
		app.executeAction(cID('setd'), desc1, dialog_mode)

	# Select
	def step303(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Select Color copy")
		desc1.putReference(cID('null'), ref1)
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(109)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Set
	def step304(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('AdjL'), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		desc2 = ps.ActionDescriptor()
		desc2.putEnumerated(sID("presetKind"), sID("presetKindType"), sID("presetKindCustom"))
		list1 = ps.ActionList()
		desc3 = ps.ActionDescriptor()
		desc3.putInteger(cID('LclR'), 1)
		desc3.putInteger(cID('BgnR'), 315)
		desc3.putInteger(cID('BgnS'), 345)
		desc3.putInteger(cID('EndS'), 15)
		desc3.putInteger(cID('EndR'), 45)
		desc3.putInteger(cID('H   '), 0)
		desc3.putInteger(cID('Strt'), -100)
		desc3.putInteger(cID('Lght'), 0)
		list1.putObject(cID('Hst2'), desc3)
		desc4 = ps.ActionDescriptor()
		desc4.putInteger(cID('LclR'), 3)
		desc4.putInteger(cID('BgnR'), 75)
		desc4.putInteger(cID('BgnS'), 105)
		desc4.putInteger(cID('EndS'), 135)
		desc4.putInteger(cID('EndR'), 165)
		desc4.putInteger(cID('H   '), 0)
		desc4.putInteger(cID('Strt'), -100)
		desc4.putInteger(cID('Lght'), 0)
		list1.putObject(cID('Hst2'), desc4)
		desc5 = ps.ActionDescriptor()
		desc5.putInteger(cID('LclR'), 4)
		desc5.putInteger(cID('BgnR'), 135)
		desc5.putInteger(cID('BgnS'), 165)
		desc5.putInteger(cID('EndS'), 195)
		desc5.putInteger(cID('EndR'), 225)
		desc5.putInteger(cID('H   '), 0)
		desc5.putInteger(cID('Strt'), -100)
		desc5.putInteger(cID('Lght'), 0)
		list1.putObject(cID('Hst2'), desc5)
		desc6 = ps.ActionDescriptor()
		desc6.putInteger(cID('LclR'), 5)
		desc6.putInteger(cID('BgnR'), 195)
		desc6.putInteger(cID('BgnS'), 225)
		desc6.putInteger(cID('EndS'), 255)
		desc6.putInteger(cID('EndR'), 285)
		desc6.putInteger(cID('H   '), 0)
		desc6.putInteger(cID('Strt'), -100)
		desc6.putInteger(cID('Lght'), 0)
		list1.putObject(cID('Hst2'), desc6)
		desc7 = ps.ActionDescriptor()
		desc7.putInteger(cID('LclR'), 6)
		desc7.putInteger(cID('BgnR'), 255)
		desc7.putInteger(cID('BgnS'), 285)
		desc7.putInteger(cID('EndS'), 315)
		desc7.putInteger(cID('EndR'), 345)
		desc7.putInteger(cID('H   '), 0)
		desc7.putInteger(cID('Strt'), -100)
		desc7.putInteger(cID('Lght'), 0)
		list1.putObject(cID('Hst2'), desc7)
		desc2.putList(cID('Adjs'), list1)
		desc1.putObject(cID('T   '), cID('HStr'), desc2)
		app.executeAction(cID('setd'), desc1, dialog_mode)

	# Select
	def step305(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Chnl'), cID('Chnl'), sID("RGB"))
		desc1.putReference(cID('null'), ref1)
		desc1.putBoolean(cID('MkVs'), False)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Set
	def step306(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		desc2 = ps.ActionDescriptor()
		desc2.putString(cID('Nm  '), "Yellows Only")
		desc1.putObject(cID('T   '), cID('Lyr '), desc2)
		app.executeAction(cID('setd'), desc1, dialog_mode)

	# Select
	def step307(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Select Color copy 2")
		desc1.putReference(cID('null'), ref1)
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(110)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Set
	def step308(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('AdjL'), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		desc2 = ps.ActionDescriptor()
		desc2.putEnumerated(sID("presetKind"), sID("presetKindType"), sID("presetKindCustom"))
		list1 = ps.ActionList()
		desc3 = ps.ActionDescriptor()
		desc3.putInteger(cID('LclR'), 1)
		desc3.putInteger(cID('BgnR'), 315)
		desc3.putInteger(cID('BgnS'), 345)
		desc3.putInteger(cID('EndS'), 15)
		desc3.putInteger(cID('EndR'), 45)
		desc3.putInteger(cID('H   '), 0)
		desc3.putInteger(cID('Strt'), -100)
		desc3.putInteger(cID('Lght'), 0)
		list1.putObject(cID('Hst2'), desc3)
		desc4 = ps.ActionDescriptor()
		desc4.putInteger(cID('LclR'), 2)
		desc4.putInteger(cID('BgnR'), 15)
		desc4.putInteger(cID('BgnS'), 45)
		desc4.putInteger(cID('EndS'), 75)
		desc4.putInteger(cID('EndR'), 105)
		desc4.putInteger(cID('H   '), 0)
		desc4.putInteger(cID('Strt'), -100)
		desc4.putInteger(cID('Lght'), 0)
		list1.putObject(cID('Hst2'), desc4)
		desc5 = ps.ActionDescriptor()
		desc5.putInteger(cID('LclR'), 4)
		desc5.putInteger(cID('BgnR'), 135)
		desc5.putInteger(cID('BgnS'), 165)
		desc5.putInteger(cID('EndS'), 195)
		desc5.putInteger(cID('EndR'), 225)
		desc5.putInteger(cID('H   '), 0)
		desc5.putInteger(cID('Strt'), -100)
		desc5.putInteger(cID('Lght'), 0)
		list1.putObject(cID('Hst2'), desc5)
		desc6 = ps.ActionDescriptor()
		desc6.putInteger(cID('LclR'), 5)
		desc6.putInteger(cID('BgnR'), 195)
		desc6.putInteger(cID('BgnS'), 225)
		desc6.putInteger(cID('EndS'), 255)
		desc6.putInteger(cID('EndR'), 285)
		desc6.putInteger(cID('H   '), 0)
		desc6.putInteger(cID('Strt'), -100)
		desc6.putInteger(cID('Lght'), 0)
		list1.putObject(cID('Hst2'), desc6)
		desc7 = ps.ActionDescriptor()
		desc7.putInteger(cID('LclR'), 6)
		desc7.putInteger(cID('BgnR'), 255)
		desc7.putInteger(cID('BgnS'), 285)
		desc7.putInteger(cID('EndS'), 315)
		desc7.putInteger(cID('EndR'), 345)
		desc7.putInteger(cID('H   '), 0)
		desc7.putInteger(cID('Strt'), -100)
		desc7.putInteger(cID('Lght'), 0)
		list1.putObject(cID('Hst2'), desc7)
		desc2.putList(cID('Adjs'), list1)
		desc1.putObject(cID('T   '), cID('HStr'), desc2)
		app.executeAction(cID('setd'), desc1, dialog_mode)

	# Select
	def step309(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Chnl'), cID('Chnl'), sID("RGB"))
		desc1.putReference(cID('null'), ref1)
		desc1.putBoolean(cID('MkVs'), False)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Set
	def step310(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		desc2 = ps.ActionDescriptor()
		desc2.putString(cID('Nm  '), "Greens Only")
		desc1.putObject(cID('T   '), cID('Lyr '), desc2)
		app.executeAction(cID('setd'), desc1, dialog_mode)

	# Select
	def step311(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Select Color copy 3")
		desc1.putReference(cID('null'), ref1)
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(111)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Set
	def step312(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('AdjL'), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		desc2 = ps.ActionDescriptor()
		desc2.putEnumerated(sID("presetKind"), sID("presetKindType"), sID("presetKindCustom"))
		list1 = ps.ActionList()
		desc3 = ps.ActionDescriptor()
		desc3.putInteger(cID('LclR'), 1)
		desc3.putInteger(cID('BgnR'), 315)
		desc3.putInteger(cID('BgnS'), 345)
		desc3.putInteger(cID('EndS'), 15)
		desc3.putInteger(cID('EndR'), 45)
		desc3.putInteger(cID('H   '), 0)
		desc3.putInteger(cID('Strt'), -100)
		desc3.putInteger(cID('Lght'), 0)
		list1.putObject(cID('Hst2'), desc3)
		desc4 = ps.ActionDescriptor()
		desc4.putInteger(cID('LclR'), 2)
		desc4.putInteger(cID('BgnR'), 15)
		desc4.putInteger(cID('BgnS'), 45)
		desc4.putInteger(cID('EndS'), 75)
		desc4.putInteger(cID('EndR'), 105)
		desc4.putInteger(cID('H   '), 0)
		desc4.putInteger(cID('Strt'), -100)
		desc4.putInteger(cID('Lght'), 0)
		list1.putObject(cID('Hst2'), desc4)
		desc5 = ps.ActionDescriptor()
		desc5.putInteger(cID('LclR'), 3)
		desc5.putInteger(cID('BgnR'), 75)
		desc5.putInteger(cID('BgnS'), 105)
		desc5.putInteger(cID('EndS'), 135)
		desc5.putInteger(cID('EndR'), 165)
		desc5.putInteger(cID('H   '), 0)
		desc5.putInteger(cID('Strt'), -100)
		desc5.putInteger(cID('Lght'), 0)
		list1.putObject(cID('Hst2'), desc5)
		desc6 = ps.ActionDescriptor()
		desc6.putInteger(cID('LclR'), 5)
		desc6.putInteger(cID('BgnR'), 195)
		desc6.putInteger(cID('BgnS'), 225)
		desc6.putInteger(cID('EndS'), 255)
		desc6.putInteger(cID('EndR'), 285)
		desc6.putInteger(cID('H   '), 0)
		desc6.putInteger(cID('Strt'), -100)
		desc6.putInteger(cID('Lght'), 0)
		list1.putObject(cID('Hst2'), desc6)
		desc7 = ps.ActionDescriptor()
		desc7.putInteger(cID('LclR'), 6)
		desc7.putInteger(cID('BgnR'), 255)
		desc7.putInteger(cID('BgnS'), 285)
		desc7.putInteger(cID('EndS'), 315)
		desc7.putInteger(cID('EndR'), 345)
		desc7.putInteger(cID('H   '), 0)
		desc7.putInteger(cID('Strt'), -100)
		desc7.putInteger(cID('Lght'), 0)
		list1.putObject(cID('Hst2'), desc7)
		desc2.putList(cID('Adjs'), list1)
		desc1.putObject(cID('T   '), cID('HStr'), desc2)
		app.executeAction(cID('setd'), desc1, dialog_mode)

	# Select
	def step313(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Chnl'), cID('Chnl'), sID("RGB"))
		desc1.putReference(cID('null'), ref1)
		desc1.putBoolean(cID('MkVs'), False)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Set
	def step314(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		desc2 = ps.ActionDescriptor()
		desc2.putString(cID('Nm  '), "Cyans Only")
		desc1.putObject(cID('T   '), cID('Lyr '), desc2)
		app.executeAction(cID('setd'), desc1, dialog_mode)

	# Select
	def step315(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Select Color copy 4")
		desc1.putReference(cID('null'), ref1)
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(112)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Set
	def step316(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('AdjL'), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		desc2 = ps.ActionDescriptor()
		desc2.putEnumerated(sID("presetKind"), sID("presetKindType"), sID("presetKindCustom"))
		list1 = ps.ActionList()
		desc3 = ps.ActionDescriptor()
		desc3.putInteger(cID('LclR'), 1)
		desc3.putInteger(cID('BgnR'), 315)
		desc3.putInteger(cID('BgnS'), 345)
		desc3.putInteger(cID('EndS'), 15)
		desc3.putInteger(cID('EndR'), 45)
		desc3.putInteger(cID('H   '), 0)
		desc3.putInteger(cID('Strt'), -100)
		desc3.putInteger(cID('Lght'), 0)
		list1.putObject(cID('Hst2'), desc3)
		desc4 = ps.ActionDescriptor()
		desc4.putInteger(cID('LclR'), 2)
		desc4.putInteger(cID('BgnR'), 15)
		desc4.putInteger(cID('BgnS'), 45)
		desc4.putInteger(cID('EndS'), 75)
		desc4.putInteger(cID('EndR'), 105)
		desc4.putInteger(cID('H   '), 0)
		desc4.putInteger(cID('Strt'), -100)
		desc4.putInteger(cID('Lght'), 0)
		list1.putObject(cID('Hst2'), desc4)
		desc5 = ps.ActionDescriptor()
		desc5.putInteger(cID('LclR'), 3)
		desc5.putInteger(cID('BgnR'), 75)
		desc5.putInteger(cID('BgnS'), 105)
		desc5.putInteger(cID('EndS'), 135)
		desc5.putInteger(cID('EndR'), 165)
		desc5.putInteger(cID('H   '), 0)
		desc5.putInteger(cID('Strt'), -100)
		desc5.putInteger(cID('Lght'), 0)
		list1.putObject(cID('Hst2'), desc5)
		desc6 = ps.ActionDescriptor()
		desc6.putInteger(cID('LclR'), 4)
		desc6.putInteger(cID('BgnR'), 135)
		desc6.putInteger(cID('BgnS'), 165)
		desc6.putInteger(cID('EndS'), 195)
		desc6.putInteger(cID('EndR'), 225)
		desc6.putInteger(cID('H   '), 0)
		desc6.putInteger(cID('Strt'), -100)
		desc6.putInteger(cID('Lght'), 0)
		list1.putObject(cID('Hst2'), desc6)
		desc7 = ps.ActionDescriptor()
		desc7.putInteger(cID('LclR'), 6)
		desc7.putInteger(cID('BgnR'), 255)
		desc7.putInteger(cID('BgnS'), 285)
		desc7.putInteger(cID('EndS'), 315)
		desc7.putInteger(cID('EndR'), 345)
		desc7.putInteger(cID('H   '), 0)
		desc7.putInteger(cID('Strt'), -100)
		desc7.putInteger(cID('Lght'), 0)
		list1.putObject(cID('Hst2'), desc7)
		desc2.putList(cID('Adjs'), list1)
		desc1.putObject(cID('T   '), cID('HStr'), desc2)
		app.executeAction(cID('setd'), desc1, dialog_mode)

	# Select
	def step317(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Chnl'), cID('Chnl'), sID("RGB"))
		desc1.putReference(cID('null'), ref1)
		desc1.putBoolean(cID('MkVs'), False)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Set
	def step318(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		desc2 = ps.ActionDescriptor()
		desc2.putString(cID('Nm  '), "Blues Only")
		desc1.putObject(cID('T   '), cID('Lyr '), desc2)
		app.executeAction(cID('setd'), desc1, dialog_mode)

	# Select
	def step319(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Select Color copy 5")
		desc1.putReference(cID('null'), ref1)
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(113)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Set
	def step320(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('AdjL'), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		desc2 = ps.ActionDescriptor()
		desc2.putEnumerated(sID("presetKind"), sID("presetKindType"), sID("presetKindCustom"))
		list1 = ps.ActionList()
		desc3 = ps.ActionDescriptor()
		desc3.putInteger(cID('LclR'), 1)
		desc3.putInteger(cID('BgnR'), 315)
		desc3.putInteger(cID('BgnS'), 345)
		desc3.putInteger(cID('EndS'), 15)
		desc3.putInteger(cID('EndR'), 45)
		desc3.putInteger(cID('H   '), 0)
		desc3.putInteger(cID('Strt'), -100)
		desc3.putInteger(cID('Lght'), 0)
		list1.putObject(cID('Hst2'), desc3)
		desc4 = ps.ActionDescriptor()
		desc4.putInteger(cID('LclR'), 2)
		desc4.putInteger(cID('BgnR'), 15)
		desc4.putInteger(cID('BgnS'), 45)
		desc4.putInteger(cID('EndS'), 75)
		desc4.putInteger(cID('EndR'), 105)
		desc4.putInteger(cID('H   '), 0)
		desc4.putInteger(cID('Strt'), -100)
		desc4.putInteger(cID('Lght'), 0)
		list1.putObject(cID('Hst2'), desc4)
		desc5 = ps.ActionDescriptor()
		desc5.putInteger(cID('LclR'), 3)
		desc5.putInteger(cID('BgnR'), 75)
		desc5.putInteger(cID('BgnS'), 105)
		desc5.putInteger(cID('EndS'), 135)
		desc5.putInteger(cID('EndR'), 165)
		desc5.putInteger(cID('H   '), 0)
		desc5.putInteger(cID('Strt'), -100)
		desc5.putInteger(cID('Lght'), 0)
		list1.putObject(cID('Hst2'), desc5)
		desc6 = ps.ActionDescriptor()
		desc6.putInteger(cID('LclR'), 4)
		desc6.putInteger(cID('BgnR'), 135)
		desc6.putInteger(cID('BgnS'), 165)
		desc6.putInteger(cID('EndS'), 195)
		desc6.putInteger(cID('EndR'), 225)
		desc6.putInteger(cID('H   '), 0)
		desc6.putInteger(cID('Strt'), -100)
		desc6.putInteger(cID('Lght'), 0)
		list1.putObject(cID('Hst2'), desc6)
		desc7 = ps.ActionDescriptor()
		desc7.putInteger(cID('LclR'), 5)
		desc7.putInteger(cID('BgnR'), 195)
		desc7.putInteger(cID('BgnS'), 225)
		desc7.putInteger(cID('EndS'), 255)
		desc7.putInteger(cID('EndR'), 285)
		desc7.putInteger(cID('H   '), 0)
		desc7.putInteger(cID('Strt'), -100)
		desc7.putInteger(cID('Lght'), 0)
		list1.putObject(cID('Hst2'), desc7)
		desc2.putList(cID('Adjs'), list1)
		desc1.putObject(cID('T   '), cID('HStr'), desc2)
		app.executeAction(cID('setd'), desc1, dialog_mode)

	# Select
	def step321(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Chnl'), cID('Chnl'), sID("RGB"))
		desc1.putReference(cID('null'), ref1)
		desc1.putBoolean(cID('MkVs'), False)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Set
	def step322(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		desc2 = ps.ActionDescriptor()
		desc2.putString(cID('Nm  '), "Magentas Only")
		desc1.putObject(cID('T   '), cID('Lyr '), desc2)
		app.executeAction(cID('setd'), desc1, dialog_mode)

	# Show
	def step323(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		list1 = ps.ActionList()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Colorize Sketch")
		list1.putReference(ref1)
		desc1.putList(cID('null'), list1)
		app.executeAction(cID('Shw '), desc1, dialog_mode)

	# Hide
	def step324(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		list1 = ps.ActionList()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Reds Only")
		ref1.putName(cID('Lyr '), "Yellows Only")
		ref1.putName(cID('Lyr '), "Greens Only")
		ref1.putName(cID('Lyr '), "Cyans Only")
		ref1.putName(cID('Lyr '), "Blues Only")
		ref1.putName(cID('Lyr '), "Magentas Only")
		list1.putReference(ref1)
		desc1.putList(cID('null'), list1)
		app.executeAction(cID('Hd  '), desc1, dialog_mode)

	# Hide
	def step325(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		list1 = ps.ActionList()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Colorize Sketch")
		list1.putReference(ref1)
		desc1.putList(cID('null'), list1)
		app.executeAction(cID('Hd  '), desc1, dialog_mode)

	# Select
	def step326(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Background Color")
		desc1.putReference(cID('null'), ref1)
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(140)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Select
	def step327(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Textures")
		desc1.putReference(cID('null'), ref1)
		desc1.putEnumerated(sID("selectionModifier"), sID("selectionModifierType"), sID("addToSelection"))
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(140)
		list1.putInteger(179)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Set
	def step328(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		desc2 = ps.ActionDescriptor()
		desc2.putEnumerated(cID('Clr '), cID('Clr '), cID('Gry '))
		desc1.putObject(cID('T   '), cID('Lyr '), desc2)
		app.executeAction(cID('setd'), desc1, dialog_mode)

	# Select
	def step329(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Overall Sharpening")
		desc1.putReference(cID('null'), ref1)
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(188)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Select
	def step330(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Overall Contrast")
		desc1.putReference(cID('null'), ref1)
		desc1.putEnumerated(sID("selectionModifier"), sID("selectionModifierType"), sID("addToSelectionContinuous"))
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(168)
		list1.putInteger(169)
		list1.putInteger(175)
		list1.putInteger(188)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Set
	def step331(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		desc2 = ps.ActionDescriptor()
		desc2.putEnumerated(cID('Clr '), cID('Clr '), cID('Vlt '))
		desc1.putObject(cID('T   '), cID('Lyr '), desc2)
		app.executeAction(cID('setd'), desc1, dialog_mode)

	# Select
	def step332(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Colorize Sketch")
		desc1.putReference(cID('null'), ref1)
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(173)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Select
	def step333(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Magentas Only")
		desc1.putReference(cID('null'), ref1)
		desc1.putEnumerated(sID("selectionModifier"), sID("selectionModifierType"), sID("addToSelectionContinuous"))
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(94)
		list1.putInteger(95)
		list1.putInteger(109)
		list1.putInteger(110)
		list1.putInteger(111)
		list1.putInteger(112)
		list1.putInteger(113)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Set
	def step334(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		desc2 = ps.ActionDescriptor()
		desc2.putEnumerated(cID('Clr '), cID('Clr '), cID('Ylw '))
		desc1.putObject(cID('T   '), cID('Lyr '), desc2)
		app.executeAction(cID('setd'), desc1, dialog_mode)

	# Select
	def step335(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Reveal Details")
		desc1.putReference(cID('null'), ref1)
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(154)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Set
	def step336(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		desc2 = ps.ActionDescriptor()
		desc2.putEnumerated(cID('Clr '), cID('Clr '), cID('Grn '))
		desc1.putObject(cID('T   '), cID('Lyr '), desc2)
		app.executeAction(cID('setd'), desc1, dialog_mode)

	# Select
	def step337(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Rough Sketch")
		desc1.putReference(cID('null'), ref1)
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(185)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Select
	def step338(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Basic Sketch")
		desc1.putReference(cID('null'), ref1)
		desc1.putEnumerated(sID("selectionModifier"), sID("selectionModifierType"), sID("addToSelectionContinuous"))
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(142)
		list1.putInteger(148)
		list1.putInteger(144)
		list1.putInteger(162)
		list1.putInteger(146)
		list1.putInteger(164)
		list1.putInteger(165)
		list1.putInteger(183)
		list1.putInteger(160)
		list1.putInteger(157)
		list1.putInteger(185)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Set
	def step339(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		desc2 = ps.ActionDescriptor()
		desc2.putEnumerated(cID('Clr '), cID('Clr '), cID('Rd  '))
		desc1.putObject(cID('T   '), cID('Lyr '), desc2)
		app.executeAction(cID('setd'), desc1, dialog_mode)

	# Select
	def step340(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Shading")
		desc1.putReference(cID('null'), ref1)
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(181)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Set
	def step341(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		desc2 = ps.ActionDescriptor()
		desc2.putEnumerated(cID('Clr '), cID('Clr '), cID('Bl  '))
		desc1.putObject(cID('T   '), cID('Lyr '), desc2)
		app.executeAction(cID('setd'), desc1, dialog_mode)

	# Select
	def step342(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Pencil Sketch")
		desc1.putReference(cID('null'), ref1)
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(177)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Select Background
	def step343(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Background")
		desc1.putReference(cID('null'), ref1)
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(1)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Merge Visible
	def step344(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		app.executeAction(sID('mergeVisible'), ps.ActionDescriptor(), dialog_mode)

	def hide(name):
		desc1 = ps.ActionDescriptor()
		list1 = ps.ActionList()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), name)
		list1.putReference(ref1)
		desc1.putList(cID('null'), list1)
		app.executeAction(cID('Hd  '), desc1, ps.DialogModes.DisplayNoDialogs)

	# Is the main layer "Layer 1"
	app.activeDocument.activeLayer.name = "Background"

	# Run each step
	step1()      # Purge
	step2()      # Reset
	step3()      # Make
	step4()      # Select
	step5()      # Make
	step6()      # Select
	step7()      # Layer Via Copy
	step8()      # Move
	step9()      # Reset
	step10()      # Filter Gallery
	step11()      # Set
	step12()      # Select
	step13()      # Layer Via Copy
	step14()      # Move
	step15()      # Reset
	step16()      # Filter Gallery
	step17()      # Set
	step18()      # Select
	step19()      # Layer Via Copy
	step20()      # Move
	step21()      # Reset
	step22()      # Filter Gallery
	step23()      # Set
	step24()      # Set
	step25()      # Select
	step26()      # Layer Via Copy
	step27()      # Move
	step28()      # Reset
	step29()      # Filter Gallery
	step30()      # Desaturate
	step31()      # Levels
	step32()      # Levels
	step33()      # Levels
	step34()      # Invert
	step35()      # Set
	step36()      # Select
	step37()      # Layer Via Copy
	step38()      # Move
	step39()      # Layer Via Copy
	step40()      # Invert
	step41()      # Gaussian Blur
	step42()      # Set
	step43()      # Select
	step44()      # Merge Layers
	step45()      # Desaturate
	step46()      # Layer Via Copy
	step47()      # Reset
	step48()      # Filter Gallery
	step49()      # Invert
	step50()      # Set
	step51()      # Set
	step52()      # Select
	step53()      # Merge Layers
	step54()      # Select
	step55()      # Layer Via Copy
	step56()      # Move
	step57()      # Desaturate
	step58()      # High Pass
	step59()      # Set
	step60()      # Set
	step61()      # Set
	step62()      # Select
	step63()      # Layer Via Copy
	step64()      # Move
	step65()      # Reset
	step66()      # Filter Gallery
	step67()      # Desaturate
	step68()      # Levels
	step69()      # Levels
	step70()      # Color Range
	step71()      # Layer Via Copy
	step72()      # Find Edges
	step73()      # Hide
	step74()      # Hide
	step75()      # Select
	step76()      # Layer Via Copy
	step77()      # Move
	step78()      # Reset
	step79()      # Filter Gallery
	step80()      # Desaturate
	step81()      # Levels
	step82()      # Levels
	step83()      # Color Range
	step84()      # Layer Via Copy
	step85()      # Find Edges
	step86()      # Select
	step87()      # Select
	step88()      # Delete
	step89()      # Select
	step90()      # Show
	step91()      # Select
	step92()      # Set
	step93()      # Set
	step94()      # Select
	step95()      # Set
	step96()      # Select
	step97()      # Move
	step98()      # Select
	step99()      # Move
	step100()      # Hide
	step101()      # Show
	step102()      # Select
	step103()      # Set
	step104()      # Select
	step105()      # Layer Via Copy
	step106()      # Move
	step107()      # Wave
	step108()      # Reset
	step109()      # Filter Gallery
	step110()      # Levels
	step111()      # Levels
	step112()      # Set
	step113()      # Set
	step114()      # Move
	step115()      # Select
	step116()      # Layer Via Copy
	step117()      # Move
	step118()      # Reset
	step119()      # Filter Gallery
	step120()      # Set
	step121()      # Layer Via Copy
	step122()      # Transform
	step123()      # Select
	step124()      # Transform
	step125()      # Select
	step126()      # Set
	step127()      # Move
	step128()      # Select
	step129()      # Select
	step130()      # Set
	step131()      # Select
	step132()      # Make
	step133()      # Fill
	step134()      # Filter Gallery
	step135()      # Set
	step136()      # Select
	step137()      # Set
	step138()      # Select
	step139()      # Make
	step140()      # Fill
	step141()      # Add Noise
	step142()      # Set
	step143()      # Set
	step144()      # Levels
	step145()      # Select
	step146()      # Move
	step147()      # Select
	step148()      # Set
	step149()      # Select

	# Rough Sketch
	step150()      # Select
	step151()      # Set

	step152()      # Select
	step153()      # Reset
	step154()      # Make
	step155()      # Set
	step156()      # Set
	step157()      # Set
	step158()      # Make
	step159()      # Set
	step160()      # Select
	step161()      # Set
	step162()      # Select
	step163()      # Layer Via Copy
	step164()      # Move
	step165()      # Reset
	step166()      # Filter Gallery
	step167()      # Set
	step168()      # Set
	step169()      # Move
	step170()      # Select
	step171()      # Layer Via Copy
	step172()      # Move
	step173()      # Set
	# step174()      # Make Select Color
	# step175()      # Create Clipping Mask
	step176()      # Hide
	step177()      # Select
	step178()      # Move
	step179()      # Select
	step180()      # Make
	step181()      # Merge Visible
	step182()      # Desaturate
	step183()      # High Pass
	step184()      # Set
	step185()      # Select
	step186()      # Select
	step187()      # Make
	step188()      # Make
	step189()      # Set
	step190()      # Select
	step191()      # Delete
	step192()      # Select
	step193()      # Set
	step194()      # Select
	step195()      # Set
	step196()      # Select
	step197()      # Set
	step198()      # Select
	step199()      # Select
	step200()      # Make
	step201()      # Make
	step202()      # Set
	step203()      # Select
	step204()      # Make
	step205()      # Select
	step206()      # Make
	step207()      # Select
	step208()      # Set
	step209()      # Select
	step210()      # Set
	step211()      # Make
	step212()      # Select
	step213()      # Make
	step214()      # Select
	step215()      # Make
	step216()      # Make
	step217()      # Set
	step218()      # Select
	step219()      # Set
	step220()      # Make
	step221()      # Select
	step222()      # Set
	step223()      # Make
	step224()      # Select
	step225()      # Set
	step226()      # Make
	step227()      # Select
	step228()      # Set
	step229()      # Select
	step230()      # Make
	step231()      # Make
	step232()      # Set
	step233()      # Select
	step234()      # Set
	step235()      # Select
	step236()      # Set
	step237()      # Select
	step238()      # Set
	step239()      # Select
	step240()      # Set
	step241()      # Select
	step242()      # Make
	step243()      # Select
	step244()      # Make
	step245()      # Select
	step246()      # Make
	step247()      # Select
	step248()      # Make

	# Rough sketch
	step249()      # Select
	step250()      # Select
	step251()      # Select
	step252()      # Make
	step253()      # Make
	step254()      # Set
	step255()      # Select
	step256()      # Set
	step257()      # Select
	step258()      # Set
	step259()      # Make
	step260()      # Select
	step261()      # Make

	step262()      # Select
	step263()      # Set
	step264()      # Make
	step265()      # Select
	step266()      # Set
	step267()      # Select
	step268()      # Set
	"""
	step269()      # Make
	step270()      # Select
	step271()      # Rename to Select Color
	"""
	step272()      # Select
	step273()      # Select
	step274()      # Set
	step275()      # Select
	step276()      # Set
	step277()      # Select
	step278()      # Set
	step279()      # Set
	step280()      # Select
	step281()      # Delete
	step282()      # Select
	step283()      # Set
	"""
	step284()      # Select
	step285()      # Merge Visible
	step286()      # Desaturate
	step287()      # High Pass
	step288()      # Set
	step289()      # Set
	step290()      # Make
	
	step291()      # Select
	step292()      # Layer Via Copy
	step293()      # Layer Via Copy
	step294()      # Layer Via Copy
	step295()      # Layer Via Copy
	step296()      # Layer Via Copy
	step297()      # Select
	step298()      # Create Clipping Mask
	step299()      # Select
	step300()      # Select
	step301()      # Set
	step302()      # Set
	step303()      # Select
	step304()      # Set
	step305()      # Select
	step306()      # Set
	step307()      # Select
	step308()      # Set
	step309()      # Select
	step310()      # Set
	step311()      # Select
	step312()      # Set
	step313()      # Select
	step314()      # Set
	step315()      # Select
	step316()      # Set
	step317()      # Select
	step318()      # Set
	step319()      # Select
	step320()      # Set
	step321()      # Select
	step322()      # Set
	step323()      # Show
	step324()      # Hide
	"""
	if not colored:
		step325()      # Hide
	"""
	step326()      # Select
	step327()      # Select
	step328()      # Set
	step329()      # Select
	step330()      # Select
	step331()      # Set
	step332()      # Select
	step333()      # Select
	step334()      # Set
	step335()      # Select
	step336()      # Set
	step337()      # Select
	step338()      # Select
	step339()      # Set
	step340()      # Select
	step341()      # Set
	step342()      # Select
	"""
	if not rough_sketch:
		hide("Rough Sketch")
	if not draft_sketch:
		hide("Draft Sketch")
	step343()      # Select BG
	step344()      # Merge
