import bpy
from bpy.types import PropertyGroup

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

#
# UI
#

class TodoPanel(bpy.types.Panel):
    bl_idname = "BLENDERTODO_PT_ToDo"
    bl_label = "Blender Todo"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "ToDo"

    def clamp(self, n):
        return max(min(20, n), 3)

    def draw(self, context):
        l = self.layout
        loc = context.scene.bl_todo
        l.template_list("TODO_UL_ToDoList", "", loc, "todo_list", loc, "index", rows=self.clamp(len(loc.todo_list) + 1), type="DEFAULT")
        r = l.row()
        r.operator("blendertodo.add", icon="ADD")
        

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




bl_classes=[TodoItem, TodoList, SceneSave, TodoPanel]

#
# OPS
#
from bpy.types import Operator

class AddItemOperator(bpy.types.Operator):
    """Add a new todo item to your list"""

    bl_idname = "blendertodo.add"
    bl_label = "Add Item"

    def execute(self, context):
        context.scene.bl_todo.todo_list.add()
        return {'FINISHED'}

class RemoveItemOperator(bpy.types.Operator):
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

class MoveItemOperator(bpy.types.Operator):
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



bl_classes.extend([AddItemOperator, RemoveItemOperator, MoveItemOperator])