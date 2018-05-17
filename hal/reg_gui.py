from Tkinter import *
import ttk

from RAL_top import *

def add_leaf(ral_branch, tree):
  for leaf in ral_branch:
    tree.insert(ral_branch.label, 'end', text=ral_branch.label, values=("","","","",""))
    
def display_gui(ral):
   
  root = Tk()
   
  tree = ttk.Treeview(root)
  tree["columns"]=("Offset","Register", "Size", "Description")
  tree.column("Offset", width=100 )
  tree.column("Register", width=100)
  tree.column("Size", width=50)
  tree.column("Description", width=800)
  tree.heading("Offset", text="Offset")
  tree.heading("Register", text="Register")
  tree.heading("Size", text="Size")
  tree.heading("Description", text="Description")

#    id = 0
#    for (subblk_label, subblk) in self.ral_item.iteritems():
#      subblk_offset_str = str(hex(subblk.offset))
#      tree.insert("", 'end', subblk_label+subblk_offset_str, text=subblk_label, value=(subblk_offset_str, "", "", "") )
#      for (blk_label, blk) in subblk.ral_item.iteritems():
#        tree.insert(subblk_label+subblk_offset_str, 'end', blk_label, text=blk_label, value=(str(hex(blk.offset)), "", "", "") )
  tree.insert("", 0, "br_reg_map", text="br_reg_map") 
  for item in ral:
    tree.insert(item, 'end', text=item, values=("","","","",""))
    add_leaf(ral.ral_item[item], tree)

  tree.pack(fill='both', expand=True)
  root.mainloop()


"""
Test program
"""
if __name__ == "__main__":  

  myRal = RAL()
  display_gui(myRal)

