# TODO List  


[] detail the Text Loom project  
[] state in simple english the steps  
# Text Loom is a node based ("code free") editor for creating nonlinear prompt based text outputs.
[] create github repo  
[] add a link to the github repo

## CODE  

[] create cli based MVP  
[] Detail each object and their nested relationships 

---

[ ] : Implement node factory *...src/backend/base_classes.py Line_494 create_node()* ←  
[ ] : Remove this node from its parent's children list *...src/backend/base_classes.py Line_507 destroy()* ←  
[ ] : Return a NodeType object instead of a string *...src/backend/base_classes.py Line_519 type()* ←  
[ ] : Return NodeType objects instead of strings *...src/backend/base_classes.py Line_524 children_type()* ←  
[ ] : Implement input name logic based on node type *...src/backend/base_classes.py Line_565 input_names()* ←  
[ ] : Implement output name logic based on node type *...src/backend/base_classes.py Line_570 output_names()* ←  
[ ] : Implement input data type logic based on node type *...src/backend/base_classes.py Line_575 input_data_types()* ←  
[ ] : Implement output data type logic based on node type *...src/backend/base_classes.py Line_580 output_data_types()* ←  
