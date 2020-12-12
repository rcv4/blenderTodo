# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name" : "BlenderTodo",
    "author" : "rcv4",
    "description" : "A Simple Blender Todo Addon",
    "blender" : (2, 83, 0),
    "version" : (0, 0, 1),
    "location" : "3D View > ToDo",
    "warning" : "",
    "category" : "Generic"
}
import bpy
from .blendertodo import SceneSave, bl_classes, view_panel_callback
from bpy.types import Scene, VIEW3D_MT_editor_menus



def register():
    for c in bl_classes:
        bpy.utils.register_class(c)

    Scene.bl_todo = bpy.props.PointerProperty(name="Blender Todo",type=SceneSave)

    VIEW3D_MT_editor_menus.append(view_panel_callback)  

def unregister():
    VIEW3D_MT_editor_menus.remove(view_panel_callback)  

    del Scene.bl_todo

    for c in reversed(bl_classes):
        bpy.utils.unregister_class(c)



