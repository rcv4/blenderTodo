import bpy
from bpy.types import PropertyGroup, Operator

# 
#  PROPS 
#

class TodoItem(PropertyGroup):
    from bpy.props import StringProperty, BoolProperty

    content: StringProperty(
        name="Title",
        default="Untitled"
    )

    done: BoolProperty(
        name="Completed",
        default=False
    )

class SceneSave(PropertyGroup):
    from bpy.props import CollectionProperty, IntProperty
    todo_list : CollectionProperty(
        type=TodoItem
    )

    index : IntProperty(
        name="Selected Todo Item", 
        default=0
    )

class Settings(bpy.types.AddonPreferences):
    bl_idname = __name__.partition('.')[0]

    from bpy.props import BoolProperty
    popover_enabled : BoolProperty(name="Show in 3D View", default=True)

    display_variants = [
        ("icon", "Icon","",1),
        ("text", "Text", "", 2)
    ]
    popover_display_as : bpy.props.EnumProperty(name="Display As", default="text", items=display_variants)

    n_panel_enabled : BoolProperty(name="Show in N-Panel", default=True)

    def draw(self, context):
        l = self.layout
        r = l.row()
        c = r.column()
        c.prop(self, "popover_enabled")
        c.prop(self, "popover_display_as")
        space = r.column()
        space.separator()
        space.separator()
        c = r.column()
        c.prop(self, "n_panel_enabled")

#
# UI
#

class TodoPanel:
    bl_region_type = "UI"
    bl_space_type = "VIEW_3D" 

    def clamp(self, n):
        return max(min(20, n), 3)

    def draw_base(self,context):
        l = self.layout
        loc = context.scene.bl_todo
        l.template_list("TODO_UL_ToDoList", "", loc, "todo_list", loc, "index", rows=self.clamp(len(loc.todo_list) + 1), type="DEFAULT")
        r = l.row()
        r.operator("blendertodo.add", icon="ADD")
        r = l.row(align=True)
        r.label(text="Move to")
        r.operator("blendertodo.top", text="Top", icon="TRIA_UP_BAR")
        r.operator("blendertodo.bottom", text="Bottom", icon="TRIA_DOWN_BAR")



class TodoIn3DPanel(TodoPanel, bpy.types.Panel):
    bl_idname = "BLENDERTODO_PT_3DView"
    bl_label = "Blender Todo"
    bl_region_type = "WINDOW"

    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):
        self.draw_base(context)

        l = self.layout
        loc = context.scene.bl_todo

        #You cant double-click to edit in popovers (https://developer.blender.org/T66286)
        if len(loc.todo_list) > 0:
            selected = loc.todo_list[loc.index]
            c = l.column(align=True)
            c.label(text="Edit: ")
            b = c.box()
            r = b.row()
            r.prop(selected, "done", text="")
            r.prop(selected, "content", text="")



class TodoInNPanel(TodoPanel, bpy.types.Panel):
    bl_idname = "BLENDERTODO_PT_NPanel"
    bl_category = "To-Do"
    bl_label = "Blender Todo"

    @classmethod
    def poll(cls, context):
        return context.preferences.addons[__name__.partition('.')[0]].preferences.n_panel_enabled

    def draw(self, context):
        self.draw_base(context)
        self.layout.separator()
        



def view_panel_callback(self, context):
    prefs = context.preferences.addons[__name__.partition('.')[0]].preferences
    if prefs.popover_enabled:
        if prefs.popover_display_as == "icon":
            self.layout.popover(TodoIn3DPanel.bl_idname, text="", icon="PRESET")
        else:
            self.layout.popover(TodoIn3DPanel.bl_idname, text="To-Do")
        
    

class TodoList(bpy.types.UIList):
    bl_idname="TODO_UL_ToDoList"

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        u = layout.row()
        c = u.column()
        c.scale_x = 0.2

        r = u.column().row(align=True)
        r.prop(item, "done", text="")
        r.prop(item, "content", text="", emboss=False)
        updown = r.column(align=True)
        updown.scale_y = 0.5
        op = updown.operator("blendertodo.move", text="", icon="TRIA_UP", emboss=False)
        op.target=index
        op.direction="UP"
        op = updown.operator("blendertodo.move", text="", icon="TRIA_DOWN", emboss=False)
        op.target=index
        op.direction="DOWN"

        op = r.operator("blendertodo.remove", text="", icon="TRASH", emboss=False)
        op.target=index

    def draw_filter(self, context, layout):
        return




bl_classes=[TodoItem, TodoList, SceneSave, Settings, TodoInNPanel, TodoIn3DPanel]

#
# OPS
#
from bpy.types import Operator

class AddItemOperator(Operator):
    """Add a new todo item to your list"""

    bl_idname = "blendertodo.add"
    bl_label = "Add Item"

    def execute(self, context):
        context.scene.bl_todo.todo_list.add()
        return {'FINISHED'}

class RemoveItemOperator(Operator):
    """Remove the item from your list"""

    bl_idname = "blendertodo.remove"
    bl_label = "Remove Item"

    target : bpy.props.IntProperty(name="Target Item Index")

    def execute(self, context):
        c_indx = context.scene.bl_todo.index
        if c_indx == self.target:
            context.scene.bl_todo.index -= (1 if c_indx > 0 else 0)

        context.scene.bl_todo.todo_list.remove(self.target)
        return {'FINISHED'}

class MoveItemOperator(Operator):
    """Move the item in your list"""

    bl_idname = "blendertodo.move"
    bl_label = "Move Item"

    target : bpy.props.IntProperty(name="Target Item Index")

    direction : bpy.props.EnumProperty(name="Direction", items=[("UP", "Up", "", 1), ("DOWN", "Down", "", 2)])

    def clamp(self, n, length):
        return max(min(length, n), 0)

    def execute(self, context):
        lst = context.scene.bl_todo.todo_list
        lgth = len(lst)

        tgt = lst[self.target]

        if self.direction == "UP":
            newindex = self.clamp(self.target - 1, lgth)
            lst.move(self.target, newindex)

        if self.direction == "DOWN":
            newindex = self.clamp(self.target + 1 , lgth)
            lst.move(self.target, newindex)

        return {'FINISHED'}

class MoveToBottomOperator(Operator):
    """Move the selected item to the bottom"""

    bl_idname = "blendertodo.bottom"
    bl_label = "Move to Bottom"

    @classmethod
    def poll(cls, context):
        return len(context.scene.bl_todo.todo_list) > 1

    def execute(self, context):
        todo = context.scene.bl_todo
        newindex = len(todo.todo_list) - 1
        todo.todo_list.move(todo.index, newindex)
        todo.index = newindex
        return {'FINISHED'}

class MoveToTopOperator(Operator):
    """Move the selected item to the top"""

    bl_idname = "blendertodo.top"
    bl_label = "Move to Top"

    @classmethod
    def poll(cls, context):
        return len(context.scene.bl_todo.todo_list) > 1

    def execute(self, context):
        todo = context.scene.bl_todo
        todo.todo_list.move(todo.index, 0)
        todo.index = 0
        return {'FINISHED'}


bl_classes.extend([AddItemOperator, RemoveItemOperator, MoveItemOperator, MoveToBottomOperator, MoveToTopOperator])