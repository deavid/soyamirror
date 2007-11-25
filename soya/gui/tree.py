# -*- coding: utf-8 -*-

# Copyright (C) 2001-2007 Jean-Baptiste LAMY -- jiba@tuxfamily
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA


# This is a port of the EditObj / EditObj2 tree widget for Tk.

import os, types
import soya, soya.gui, soya.opengl as opengl, soya.sdlconst as sdlconst


class Node(object):
  """Tree's Node base class. You must inherit this class and override a few method :
 - get_text()                           -> unicode : must return the Node's label.
 - get_material()                       -> material: must return the Node's material (used as a texture for icon).
 - create_children(old_children = None) -> list    : (Optionnal) called the first time we need the children; must return a list of child Node. oldchildren may contains the previous children, in case of an update.
 - is_expandable()                      -> boolean : (Optionnal) must return true if this Node has children.
 - get_height()                         -> height  : (Optionnal) override this if you use non-regular height.

The "icon_width" attribute define the width of the icon. You can override it in geticon(), e.g. just before returning the icon, do 'self.icon_width = icon.width()'.
It defaults to 20.

If you override __init__(), you must call Node.__init__(parent), AT THE END OF YOUR __init__() !
"""
  
  def __init__(self, parent):
    """Create a new Node. Parent can be either the parent's Node, or the tree (for the root Node).
If you override __init__(), you must call Node.__init__(parent), AT THE END OF YOUR __init__() !
"""
    if isinstance(parent, Node):
      self.parent         = parent
      self.tree           = parent.tree
      self.depth          = parent.depth + 1
    else:
      self.parent         = None
      self.tree           = parent
      self.depth          = 0
    self.children         = []
    self.children_created = 0
    self.expanded         = 0
    self.selected         = 0
    self.highlight        = 0
    self._display_list    = soya.DisplayList()
    self.icon_width       = self.tree.icon_width
    self.icon_height      = self.tree.icon_height
    self.text             = self.get_text()
    self.material         = self.get_material()
    self.changed          = -2
    
    if not self.parent: self.tree._set_node(self) # Root Node must be passed to the tree.
    self.calc_size()
    
  def calc_size(self, y = 0):
    self.x           = self.depth * soya.gui.widgets.STYLE.char_height
    self.height      = max(soya.gui.widgets.STYLE.char_height, self.icon_height) + 5
    self.width       = self.x + soya.gui.widgets.STYLE.char_height + 4 + self.icon_width + 4 + int(self.tree.font.get_print_size(self.text)[0])
    
  def calc_tree_size(self):
    if self.tree.ideal_width < self.width: self.tree.ideal_width = self.width
    self.tree.ideal_height += self.height
    if self.expanded:
      for child in self.children: child.calc_tree_size()
      
  def render(self):
    if self.tree.render_y >= self.tree.render_y2: return
    
    if self.tree.render_y >= self.tree.render_y1 - self.height:
      if self.selected:
        soya.gui.widgets.STYLE.rectangle(-1, -1, self.tree.visible_width, self.height - 3, self.highlight or self.tree.focus)
        
      if soya.gui.widgets.STYLE.char_height < self.icon_height:
        y0 = (self.icon_height - soya.gui.widgets.STYLE.char_height) // 2
      else: y0 = 0
      
      if self.is_expandable():
        if self.expanded:
          soya.gui.widgets.STYLE.triangle(3, self.x, y0, self.x + soya.gui.widgets.STYLE.char_height, y0 + soya.gui.widgets.STYLE.char_height, self.highlight)
        else:
          soya.gui.widgets.STYLE.triangle(1, self.x, y0, self.x + soya.gui.widgets.STYLE.char_height, y0 + soya.gui.widgets.STYLE.char_height, self.highlight)
          
      if self.material:
        x1 = self.x + soya.gui.widgets.STYLE.char_height + 4
        x2 = x1 + self.icon_width
        self.material.activate()
        if self.material.is_alpha(): opengl.glEnable(opengl.GL_BLEND)
        opengl.glBegin   (opengl.GL_QUADS)
        opengl.glTexCoord2f(0.0, 0.0); opengl.glVertex2i(x1, 0)
        opengl.glTexCoord2f(0.0, 1.0); opengl.glVertex2i(x1, self.icon_height)
        opengl.glTexCoord2f(1.0, 1.0); opengl.glVertex2i(x2, self.icon_height)
        opengl.glTexCoord2f(1.0, 0.0); opengl.glVertex2i(x2, 0)
        opengl.glEnd()
        soya.DEFAULT_MATERIAL.activate()
        
      opengl.glColor4f(*soya.gui.widgets.STYLE.text_colors[self.highlight])
      if self.changed != self.tree.font._pixels_height:
        self.tree.font.create_glyphs(self.text)
        
        opengl.glNewList(self._display_list.id, opengl.GL_COMPILE_AND_EXECUTE)
        self.tree.font.draw(self.text, self.x + soya.gui.widgets.STYLE.char_height + 8 + self.icon_width, y0)
        opengl.glEndList()
        self._changed = self.tree.font._pixels_height
      else:
        opengl.glCallList(self._display_list.id)
        
    self.tree.render_y += self.height
    opengl.glTranslatef(0.0, self.height, 0.0)
    
    if self.expanded:
      for child in self.children: child.render()
      
  def create_children(self, old_children = None): return self.children
  
  def last_child(self):
    if self.children_created and self.expanded: return self.children[-1].last_child()
    else: return self
  def previous(self):
    if isinstance(self.parent, Node):
      if self.index == 0: return self.parent
      return self.parent.children[self.index - 1].last_child()
    else: return None # Root Node
  def next(self):
    if self.expanded and self.children:
      return self.children[0]
    else:
      if isinstance(self.parent, Node): return self.parent._next(self)
      else: return None # Root Node
  def _next(self, node):
    if node.index + 1 >= len(self.children):
      if isinstance(self.parent, Node): return self.parent._next(self)
      else: return None # Root Node
    return self.children[node.index + 1]
    
  def update(self):
    self.changed  = -2
    self.text     = self.get_text()
    self.material = self.get_material()
    
  def update_tree(self):
    self.update()
    for child in self.children: child.update_tree()
  def update_children(self):
    if self.children_created:
      if self.expanded:
        old_children = self.children
        for child in self.children: child._undraw()
        self.children = self.create_children(self.children)
        i = 0
        if self.children:
          for child in self.children:
            child.index = i
            i = i + 1
        else:
          self.expanded = 0 # Cannot be expanded if no children
        self.tree.draw()
      else:
        self.children = []
        self.children_created = 0
        
  def set_selected(self, selected):
    if selected != self.selected:
      if selected:
        self.tree.deselect_all()
        self.selected = 1
        self.tree.selection.append(self)
      else:
        self.selected = 0
        self.tree.selection.remove(self)
        
  def expand(self):
    if not self.expanded:
      if not self.children_created:
        self.children = self.create_children()
        i = 0
        for child in self.children:
          child.index = i
          i = i + 1
        self.children_created = 1
      if len(self.children) > 0:
        self.expanded = 1
        self.tree.request_resize()
        
  def collapse(self):
    if self.expanded:
      self.expanded = 0
      self.tree.request_resize()
      
  def is_expandable(self): return len(self.children)
  def toggle(self):
    if self.expanded: self.collapse()
    else: self.expand()
    
  def get_text    (self): return self.text
  def get_material(self): return self.material
  
  def get_at_y(self):
    self.tree.current_y -= self.height
    if self.tree.current_y <= 0: return self
    
    if self.expanded:
      last = None
      for child in self.children:
        if last and (self.tree.current_y < 0) and last.get_at_y(): return last
        self.tree.current_y -= child.height
        last = child
        
  def on_mouse_pressed(self, button, x, y):
    if button == 1:
      if self.tree.render_y <= y <= self.tree.render_y + self.height:
        if self.is_expandable() and (self.selected or (self.x <= x <= self.x + soya.gui.widgets.STYLE.char_height)):
          self.toggle()
        else:
          self.set_selected(1)
        self.tree.render_y += self.height
        return 1
      else:
        self.tree.render_y += self.height
        
        if self.expanded:
          for child in self.children:
            if child.on_mouse_pressed(button, x, y): return 1
            
  def on_mouse_move(self, x, y, x_relative, y_relative, state):
    if self.tree.render_y <= y <= self.tree.render_y + self.height:
      self.set_highlight(1)
      self.tree.render_y += self.height
      return 1
    else:
      self.tree.render_y += self.height
      
      if self.expanded:
        for child in self.children:
          if child.on_mouse_move(x, y, x_relative, y_relative, state): return 1
          
        
  def set_highlight(self, highlight):
    if highlight:
      if soya.gui.widgets.HIGHLIGHT_WIDGET: soya.gui.widgets.HIGHLIGHT_WIDGET.set_highlight(0)
      self.highlight = 1
      soya.gui.widgets.HIGHLIGHT_WIDGET = self
    else:
      self.highlight = 0
      soya.gui.widgets.HIGHLIGHT_WIDGET = None
    return 1
      
class SimpleNode(Node):
  def __init__(self, parent, text = u"", material = None):
    self.text     = text
    self.material = material
    Node.__init__(self, parent)
    if isinstance(parent, SimpleNode):
      self.index = len(self.parent.children)
      parent.children.append(self)
    
    
class Tree(soya.gui.HighlightableWidget, soya.gui.FocusableWidget):
  """Tree widget
First create a Tree widget.
Then create a root Node, by passing the tree as parent (= the first arg of the constructor).

>>> root = Tk()
>>> tree = Tree(root)
>>> tree.frame.pack(expand = 1, fill = "both")
>>> node = YourNode(tree [, your Node's data])
>>> root.mainloop()
"""
  
  def __init__(self, parent, font = None):
    soya.gui.Widget.__init__(self, parent)
    soya.gui.FocusableWidget.__init__(self)
    self.node_height  = soya.gui.widgets.STYLE.char_height
    self.size_tree    = 0
    self.node         = None
    self.first        = None
    self.ny           = 0
    self.selection    = []
    self.displayed    = []
    self.font         = font or soya.gui.widgets.STYLE.font
    self.icon_width   = soya.gui.widgets.STYLE.char_height * 2
    self.icon_height  = soya.gui.widgets.STYLE.char_height * 2
    
  def _set_node(self, node):
    node.index     = 0
    self.node      = node
    self.first     = node
    self.ny        = 0
    self.size_tree = 0
    self.selection = []
    self.displayed = []
    if node: node.expand()
    
  def calc_size(self):
    self.ideal_width  = 0
    self.ideal_height = 0
    if self.node: self.node.calc_tree_size()
    self.min_width  = self.ideal_width
    self.min_height = self.ideal_height
    self.ideal_width  += 4
    
  def update_tree(self):
    if self.node:
      self.node.update()
      self.request_resize()
      
  def allocate(self, x, y, width, height):
    soya.gui.Widget.allocate(self, x, y, width, height)
    if isinstance(self.parent, soya.gui.ScrollPane): self.visible_width = self.parent.col_widths[0] - 3
    else:                                            self.visible_width = self.width
    
  def _init_walk(self):
    if self.node:
      self.render_y = 2
      if isinstance(self.parent, soya.gui.ScrollPane):
        self.render_y1 = self.parent.vscroll.value
        self.render_y2 = self.render_y1 + self.parent.row_heights[0]
      else:
        self.render_y1 = 0
        self.render_y2 = self.render_y1 + self.height
      return 1
    
  def render(self):
    if self._init_walk():
      opengl.glPushMatrix()
      opengl.glTranslatef(self.x + 2, self.y + 2, 0.0)
      self.node.render()
      opengl.glPopMatrix()
      
  def deselect_all(self):
    """Deselect all selected Nodes."""
    if self.selection:
      for node in self.selection[:]: node.set_selected(0)
      
  def on_mouse_pressed (self, button, x, y):
    if self._init_walk(): self.node.on_mouse_pressed (button, x - self.x - 2, y - self.y)
    if button == 1:
      self.set_focus(1)
      return 1
    
  def on_mouse_move(self, x, y, x_relative, y_relative, state):
    if self._init_walk(): self.node.on_mouse_move(x - self.x - 2, y - self.y, x_relative, y_relative, state)
    return 1
  
  def set_highlight(self, highlight): pass
  
  def on_key_pressed (self, key, mods, unicode_key = 0):
    if   key == sdlconst.K_UP:
      if self.selection:
        node = self.selection[0].previous()
        if node: node.set_selected(1)
        
    elif key == sdlconst.K_DOWN:
      if self.selection:
        node = self.selection[0].next()
        if node: node.set_selected(1)
        
    elif key == sdlconst.K_LEFT:
      if self.selection and self.selection[0].is_expandable(): self.selection[0].collapse()
      
    elif key == sdlconst.K_RIGHT:
      if self.selection and self.selection[0].is_expandable(): self.selection[0].expand()
      

