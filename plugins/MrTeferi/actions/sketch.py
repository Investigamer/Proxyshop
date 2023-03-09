"""
Sketchify Action Module
"""
import photoshop.api as ps
app = ps.Application()
cID = app.charIDToTypeID
sID = app.stringIDToTypeID


def run():
	"""
	NewSketchify Steps
	"""

	# Duplicate
	def step1(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putProperty(cID('Lyr '), cID('Bckg'))
		desc1.putReference(cID('null'), ref1)
		desc1.putString(cID('Nm  '), "Layer 1 copy")
		desc1.putInteger(cID('Vrsn'), 5)
		app.executeAction(cID('Dplc'), desc1, dialog_mode)

	# Invert
	def step2(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		app.executeAction(cID('Invr'), ps.ActionDescriptor(), dialog_mode)

	# Gaussian Blur
	def step3(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		desc1.putUnitDouble(cID('Rds '), cID('#Pxl'), 65)
		app.executeAction(sID('gaussianBlur'), desc1, dialog_mode)

	# Set
	def step4(enabled=True, dialog=False):
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

	# Make
	def step5(enabled=True, dialog=False):
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
	def step6(enabled=True, dialog=False):
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
		list2 = ps.ActionList()
		list2.putInteger(91)
		list2.putInteger(255)
		desc3.putList(cID('Inpt'), list2)
		desc3.putDouble(cID('Gmm '), 0.66)
		list1.putObject(cID('LvlA'), desc3)
		desc2.putList(cID('Adjs'), list1)
		desc1.putObject(cID('T   '), cID('Lvls'), desc2)
		app.executeAction(cID('setd'), desc1, dialog_mode)

	# Make
	def step7(enabled=True, dialog=False):
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
		desc3.putInteger(cID('Rd  '), 40)
		desc3.putInteger(cID('Yllw'), 60)
		desc3.putInteger(cID('Grn '), 40)
		desc3.putInteger(cID('Cyn '), 60)
		desc3.putInteger(cID('Bl  '), 20)
		desc3.putInteger(cID('Mgnt'), 80)
		desc3.putBoolean(sID("useTint"), False)
		desc4 = ps.ActionDescriptor()
		desc4.putDouble(cID('Rd  '), 225)
		desc4.putDouble(cID('Grn '), 211)
		desc4.putDouble(cID('Bl  '), 179)
		desc3.putObject(sID("tintColor"), sID("RGBColor"), desc4)
		desc2.putObject(cID('Type'), cID('BanW'), desc3)
		desc1.putObject(cID('Usng'), cID('AdjL'), desc2)
		app.executeAction(cID('Mk  '), desc1, dialog_mode)

	# Set
	def step8(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putProperty(cID('Chnl'), sID("selection"))
		desc1.putReference(cID('null'), ref1)
		desc1.putEnumerated(cID('T   '), cID('Ordn'), cID('Al  '))
		app.executeAction(cID('setd'), desc1, dialog_mode)

	# Copy Merged
	def step9(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		app.executeAction(sID('copyMerged'), ps.ActionDescriptor(), dialog_mode)

	# Paste
	def step10(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		desc1.putEnumerated(cID('AntA'), cID('Annt'), cID('Anno'))
		desc1.putClass(cID('As  '), cID('Pxel'))
		app.executeAction(cID('past'), desc1, dialog_mode)

	# Filter Gallery
	def step11(enabled=True, dialog=False):
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
	def step12(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		app.executeAction(cID('Invr'), ps.ActionDescriptor(), dialog_mode)

	# Set
	def step13(enabled=True, dialog=False):
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
	def step14(enabled=True, dialog=False):
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
	def step15(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Black & White 1")
		desc1.putReference(cID('null'), ref1)
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(6)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Make
	def step16(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putClass(cID('Lyr '))
		desc1.putReference(cID('null'), ref1)
		desc1.putInteger(cID('LyrI'), 8)
		app.executeAction(cID('Mk  '), desc1, dialog_mode)

	# Select
	def step17(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Layer 2")
		desc1.putReference(cID('null'), ref1)
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(7)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

	# Fill
	def step18(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		desc1.putEnumerated(cID('Usng'), cID('FlCn'), cID('BckC'))
		app.executeAction(cID('Fl  '), desc1, dialog_mode)

	# Filter Gallery
	def step19(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		desc1.putEnumerated(cID('GEfk'), cID('GEft'), cID('Txtz'))
		desc1.putEnumerated(cID('TxtT'), cID('TxtT'), cID('TxSt'))
		desc1.putInteger(cID('Scln'), 100)
		desc1.putInteger(cID('Rlf '), 4)
		desc1.putEnumerated(cID('LghD'), cID('LghD'), cID('LDTp'))
		desc1.putBoolean(cID('InvT'), False)
		app.executeAction(1195730531, desc1, dialog_mode)

	# Set
	def step20(enabled=True, dialog=False):
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
	def step21(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		desc2 = ps.ActionDescriptor()
		desc2.putUnitDouble(cID('Opct'), cID('#Prc'), 70)
		desc1.putObject(cID('T   '), cID('Lyr '), desc2)
		app.executeAction(cID('setd'), desc1, dialog_mode)

	# Select
	def step22(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putName(cID('Lyr '), "Black & White 1")
		desc1.putReference(cID('null'), ref1)
		desc1.putBoolean(cID('MkVs'), False)
		list1 = ps.ActionList()
		list1.putInteger(6)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('slct'), desc1, dialog_mode)

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
		desc2.putUnitDouble(cID('Opct'), cID('#Prc'), 50)
		desc1.putObject(cID('T   '), cID('Lyr '), desc2)
		app.executeAction(cID('setd'), desc1, dialog_mode)

	# Select
	def step24(enabled=True, dialog=False):
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

	# Duplicate
	def step25(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		desc1.putString(cID('Nm  '), "top adjustment")
		desc1.putInteger(cID('Vrsn'), 5)
		list1 = ps.ActionList()
		list1.putInteger(35)
		desc1.putList(cID('Idnt'), list1)
		app.executeAction(cID('Dplc'), desc1, dialog_mode)

	# Move
	def step26(enabled=True, dialog=False):
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
		list1.putInteger(35)
		desc1.putList(cID('LyrI'), list1)
		app.executeAction(cID('move'), desc1, dialog_mode)

	# Set
	def step27(enabled=True, dialog=False):
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

	# Set
	def step28(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		desc1 = ps.ActionDescriptor()
		ref1 = ps.ActionReference()
		ref1.putEnumerated(cID('Lyr '), cID('Ordn'), cID('Trgt'))
		desc1.putReference(cID('null'), ref1)
		desc2 = ps.ActionDescriptor()
		desc2.putEnumerated(cID('Md  '), cID('BlnM'), cID('HrdL'))
		desc1.putObject(cID('T   '), cID('Lyr '), desc2)
		app.executeAction(cID('setd'), desc1, dialog_mode)

	# Merge Visible
	def step29(enabled=True, dialog=False):
		if not enabled: return
		if dialog: dialog_mode = ps.DialogModes.DisplayAllDialogs
		else: dialog_mode = ps.DialogModes.DisplayNoDialogs
		app.executeAction(sID('mergeVisible'), ps.ActionDescriptor(), dialog_mode)

	# Run each step
	step1()      # Duplicate
	step2()      # Invert
	step3()      # Gaussian Blur
	step4()      # Set
	step5()      # Make
	step6()      # Set
	step7()      # Make
	step8()      # Set
	step9()      # Copy Merged
	step10()      # Paste
	step11()      # Filter Gallery
	step12()      # Invert
	step13()      # Set
	step14()      # Set
	step15()      # Select
	step16()      # Make
	step17()      # Select
	step18()      # Fill
	step19()      # Filter Gallery
	step20()      # Set
	step21()      # Set
	step22()      # Select
	step23()      # Set
	step24()      # Select
	step25()      # Duplicate
	step26()      # Move
	step27()      # Set
	step28()      # Set
	step29()      # Merge
