# # pylint: disable=missing-function-docstring
# # pylint: disable=missing-class-docstring
# # pylint: disable=line-too-long
# '''
#     Methods for managing drawio diagrams.

#     ----------

#     Meta
#     ----------
#     `author`: Colemen Atwood
#     `created`: 06-04-2022 15:45:00
#     `memberOf`: drawio
#     `name`: diagram
# '''

# from typing import Iterable,TypeVar
# from lxml import etree as _etree

# import utils.string_utils as _csu
# import utils.drawio.diagram_utils as _dia

# import utils.drawio.mcxell as _mxcell_module
# import utils.drawio.onode as _onode_module
# import utils.drawio.connector as connector_module
# import utils.drawio.drawing as _Drawing



# _new_mxcell = _mxcell_module.new_mxcell
# _Mxcell = _mxcell_module.Mxcell

# _Onode = _onode_module.Onode
# _new_onode = _onode_module.new_onode

# _Connector = connector_module.Connector
# _new_connector = connector_module.new_connector


# _onode_type = TypeVar('_onode_type', bound=_Onode)
# _connector_type = TypeVar('_connector_type', bound=_Connector)
# _mxcell_type = TypeVar('_mxcell_type', bound=_Mxcell)
# element_type = TypeVar('element_type', bound=_etree.Element)




# class Diagram:
#     '''
#         Manages a drawio diagram.
#         The diagrams contains the nodes and appear as tabs in the drawing.

#         ----------

#         Arguments
#         -------------------------
#         `tree` {etree}
#             The drawing xml tree.
#         `element` {element}
#             The etree element that will be added to the drawing.
#             The new_diagram method generates this automatically.

#         Meta
#         ----------
#         `author`: Colemen Atwood
#         `created`: 06-04-2022 16:47:17
#         `memberOf`: diagram
#         `version`: 1.0
#         `method_name`: Diagram
#         * @xxx [06-04-2022 16:49:56]: documentation for Diagram
#     '''


#     def __init__(self,tree:_etree,element=None):
#         self.settings = {}
#         self.tree = tree
#         self.element = element
#         self.dia_root = None
#         self.data = {
#             "attributes":{},
#             "connectors":[],
#             "mxcells":[],
#             "onodes":[],
#             "children":[],
#         }

#         self._from_element()
#         # self.set_defaults()

#     def _from_element(self):
#         element = self.element
#         if element is not None:
#             root_list:Iterable = _dia.get_diagram_root_node(element)
#             if len(root_list) > 0:
#                 dia_root = root_list[0]
#                 self.dia_root = dia_root
#             self.data['attributes'] = _dia.attrib_to_dict(element.attrib)
#             # self.data['connectors'] = _dia.get_connectors(element)
#             children = _dia.get_children(self.dia_root)
#             # print(f"children: {children}")
#             for c in children:
#                 if c.tag == "mxCell":
#                     if 'source' in c.attrib:
#                         con = _Connector(self.tree,c,self)
#                         self.data['connectors'].append(con)
#                         # self.data['connectors']
#                         # print(f"connector Found: {c}")
#                     else:
#                         self.data['mxcells'].append(_Mxcell(self.tree,c,self))
#                         # print(f"mxcell found: {c}")

#                 if c.tag == "object":
#                     O = _Onode(self.tree,c,self)
#                     self.data['onodes'].append(O)
#                     # print(f"object found: {c}")
#                 # self.data['children']['id'] = c.attrib['id']

#             return self.data

#     def show_grid(self,value:bool):
#         if value is True:
#             self.element.attrib['grid'] = "1"
#         if value is False:
#             self.element.attrib['grid'] = "0"

#     def grid_size(self,value:int):
#         if value < 1:
#             value = 10
#         self.element.attrib['gridSize'] = str(value)

#     def list_node_labels(self):
#         '''
#             Print the labels of every node in this diagram.

#             ----------


#             Return {None}
#             ----------------------
#             returns nothing.

#             Meta
#             ----------
#             `author`: Colemen Atwood
#             `created`: 05-27-2022 12:45:59
#             `memberOf`: diagram
#             `version`: 1.0
#             `method_name`: list_node_labels
#         '''
#         x:_Onode
#         for x in self.data['onodes']:
#             label = x.get_label(None)
#             if label is not None:
#                 print(label)

#         x:_Mxcell
#         for x in self.data['mxcells']:
#             label = x.get_label(None)
#             if label is not None:
#                 print(label)

#         x:_Connector
#         for x in self.data['connectors']:
#             label = x.get_label(None)
#             if label is not None:
#                 print(label)

#     def add_mxcell(self,id=None,parent=None)->_mxcell_type:
#         cell = _new_mxcell(self.tree,self,id,parent)
#         self.data['mxcells'].append(cell)
#         return cell

#     def add_onode(self,id=None)->_onode_type:
#         cell = _new_onode(self.tree,self,id)
#         self.data['onodes'].append(cell)
#         return cell

#     def add_connector(self,source,target)->_connector_type:
#         cell = _new_connector(self.tree,self,source,target)
#         self.data['connectors'].append(cell)
#         return cell

#     def get_nodes_by_tag(self,tag)->Iterable[_Onode]:
#         '''
#             Get all nodes that contain the tag provided.

#             ----------

#             Arguments
#             -------------------------
#             `tag` {str|list}
#                 The tag or list of tags to search for.


#             Return {list}
#             ----------------------
#             A list of onodes that contain the tag.
#             Only object nodes support the tags attribute, so this will not include mxcells or connectors.

#             Meta
#             ----------
#             `author`: Colemen Atwood
#             `created`: 05-27-2022 13:36:21
#             `memberOf`: diagram
#             `version`: 1.0
#             `method_name`: get_nodes_by_tag
#         '''

#         nodes = []
#         c:_Onode
#         for c in self.data['onodes']:
#             if c.has_tag(tag):
#                 nodes.append(c)
#         return nodes


#     def set_name(self,name:str):
#         '''
#             Set this diagrams name.

#             ----------

#             Arguments
#             -------------------------
#             `name` {str}
#                 The new name to assign.

#             Return {None}
#             ----------------------
#             returns nothing

#             Meta
#             ----------
#             `author`: Colemen Atwood
#             `created`: 05-27-2022 13:38:58
#             `memberOf`: diagram
#             `version`: 1.0
#             `method_name`: set_name
#         '''

#         self.data['attributes']['name'] = name
#         self.element.attrib['name'] = name

#     def get_name(self,test_value=None,default_val=False):
#         '''
#             Get the name attribute of the diagram.

#             ----------

#             Arguments
#             -------------------------
#             [`test_value`=None] {str}
#                 If provided, the name value must match this in order to return positively.

#             [`default_val`=''] {any}
#                 The value to return of the name does not exist or does not match the test_value.


#             Return {any}
#             ----------------------
#             If no test_value is provided the name value is returned.
#             If a test_value is provided and the name value matches, the name is returned.

#             If the name attribute does not exist or does not match the test_value,
#             the default_val is returned.

#             Meta
#             ----------
#             `author`: Colemen Atwood
#             `created`: 05-27-2022 11:55:25
#             `memberOf`: nodeBase
#             `version`: 1.0
#             `method_name`: get_name
#         '''

#         if 'name' in self.data['attributes']:
#             if test_value is not None:
#                 if self.data['attributes']['name'] == test_value:
#                     return self.data['attributes']['name']
#             else:
#                 return self.data['attributes']['name']
#         return default_val


#     def has_name(self,name=None):
#         if 'name' in self.data['attributes']:
#             if name is not None:
#                 if self.data['attributes']['name'] == name:
#                     return True
#             return True
#         return False


# def new_diagram(drawing:_Drawing,name:str)->Diagram:
#     '''
#         Create a new diagram in the drawing.

#         ----------

#         Arguments
#         -------------------------
#         `drawing` {Drawing}
#             A reference to the drawing that this diagram will belong to.
#         `name` {str}
#             The name of the diagram, this is shown on the tabs in draw.io

#         Return {Diagram}
#         ----------------------
#         An instance of the Diagram class

#         Meta
#         ----------
#         `author`: Colemen Atwood
#         `created`: 05-27-2022 12:42:40
#         `memberOf`: diagram
#         `version`: 1.0
#         `method_name`: new_diagram
#     '''

#     diagram = _etree.SubElement(drawing, 'diagram')
#     # diagram = _etree.Element("diagram")

#     diagram.attrib['id'] = _csu.gen.rand(20)
#     diagram.attrib['name'] = name

#     mxgm_data = {
#         "dx":"1074",
#         "dy":"954",
#         "grid":"1",
#         "gridSize":"10",
#         "guides":"1",
#         "tooltips":"1",
#         "connect":"1",
#         "arrows":"1",
#         "fold":"1",
#         "page":"1",
#         "pageScale":"1",
#         "pageWidth":"1700",
#         "pageHeight":"1100",
#         "math":"0",
#         "shadow":"0",
#     }

#     mxGraphModel = _etree.SubElement(diagram, 'mxGraphModel')
#     for k,v in mxgm_data.items():
#         mxGraphModel.attrib[k] = v

#     # @Mstep [] create the root node for the diagram
#     root = _etree.SubElement(mxGraphModel, 'root')


#     d = Diagram(drawing,diagram)

#     # @Mstep [] add the two default nodes to the diagram.
#     d.add_mxcell("0")
#     d.add_mxcell("1","0")

#     # @Mstep [RETURN] return the diagram instance.
#     return d



