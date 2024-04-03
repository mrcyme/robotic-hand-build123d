# %%
import yaml
from build123d import *
from ocp_vscode import *
import math
import yaml
# Load parameters from YAML file
with open('parameters.yaml', 'r') as file:
    params = yaml.safe_load(file)
joint_radius = params['joint']['radius']
joint_offset = params['joint']['offset']
joint_thickness = params['joint']['thickness']
finger_thickness = params['global']['finger_thickness']
thumb = params['thumb']
fingers = params['fingers']
palm_width = params['palm']['width']
palm_height = params['palm']['height']
palm_thickness = params['palm']['thickness']
palm_angle = params['palm']['angle']
thumb_height_offset = params['palm']['thumb_height_offset']
palm_joint_thickness= params['palm']['joint_thickness']
palm_thumb_width = params['palm']['thumb_width']
palm_joint_radius = params['palm']['joint_radius']
palm_joint_offset = params['palm']['joint_offset']
fillet_radius = params['global']['fillet_radius']

# intermediate variables
d = math.tan(math.radians(palm_angle))*(palm_height-thumb_height_offset)
inter_finger_offset = (palm_width-4*finger_thickness)/3


# Function to fillet all edges of a shape
def fillet_all_edges(shape, radius):
    return fillet(shape.edges(), radius=radius)



# Define the points for the palm and thumb palm
palm_points = [(0, 0), (0, palm_height), (palm_width, palm_height), (palm_width, palm_height-thumb_height_offset), (palm_width-d, 0)]
thumb_palm_points = [(0, 0), (d, palm_height-thumb_height_offset), (d+palm_thumb_width, palm_height-thumb_height_offset), (palm_thumb_width, 0)]

# Create the palm
palm = fillet_all_edges(extrude(Polygon(*palm_points, align= (Align.MIN, Align.MIN)), palm_thickness/2, both=True), fillet_radius)
palm.label = "palm"
# Create the thumb palm
thumb_palm = fillet_all_edges(Pos(X=palm_width-d+palm_joint_offset)*extrude(Polygon(*thumb_palm_points, align= (Align.MIN, Align.MIN)), palm_thickness/2, both=True), radius=fillet_radius) 
thumb_palm.label = "little_palm"
#create the palm joint
palm_joint = Pos(palm_width-d+d/2+palm_joint_radius,(palm_height-thumb_height_offset)/2,0)* Rot(90, -palm_angle,0)*Cylinder(palm_joint_radius, palm_joint_thickness)
palm_joint.label = "palm_joint"
palm_collection = Pos(X=-palm_width)*Compound(label="palm", children=[palm, thumb_palm, palm_joint])



fingers_list = []
z_current = 0 
# Loop through each finger
for finger_key, finger in fingers.items():
    phalanges = []
    x_current = 0  # Initialize the x position
    i=1
    #connection joint with the palm
    j = extrude(Pos(x_current - joint_offset, 0, z_current) * Circle(joint_radius), joint_thickness)
    j.label = "palm_finger_joint"
    phalanges.append(j)
    # Loop through each phalanx in the finger
    for phalanx_key, phalanx in finger.items():
        x_radius = phalanx['x_radius']
        y_radius = phalanx['y_radius']
        # Create the phalanx
        p = fillet_all_edges(extrude(Pos(x_current+x_radius, 0, z_current) * Ellipse(x_radius, y_radius), finger_thickness), fillet_radius)
        p.label = phalanx_key
        phalanges.append(p)
        x_current += 2*x_radius + joint_offset
        
        # Add palm_width joint after each phalanx except the last
        if phalanx_key != list(finger.keys())[-1]:
            j = extrude(Pos(x_current - joint_offset, 0, z_current) * Circle(joint_radius), joint_thickness)
            j.label = f"interphalange_joint_{i}"
            phalanges.append(j)
            x_current += joint_offset  # Update for the joint
        i+=1
    finger = Compound(label=finger_key, children=phalanges)
    fingers_list.append(finger)
    z_current+=inter_finger_offset + finger_thickness
    

z_current = - palm_joint_offset - finger_thickness - finger_thickness/2
x_current = 0  # Initialize the x position
phalanges = []
i=1
for phalanx_key, phalanx in thumb.items():
    x_radius = phalanx['x_radius']
    y_radius = phalanx['y_radius']
    #connection joint with the palm
    j = extrude(Pos(x_current - joint_offset-thumb_height_offset, 0, z_current) * Circle(joint_radius), joint_thickness)
    j.label = f"thumb_joint_{i}"
    phalanges.append(j)
    # Create the phalanx
    p = fillet_all_edges(extrude(Pos(x_current+x_radius-thumb_height_offset, 0, z_current) * Ellipse(x_radius, y_radius), finger_thickness), fillet_radius)
    p.label = phalanx_key
    phalanges.append(p)
    x_current += 2*x_radius + joint_offset
    i+=1
finger = Compound(label="thumb", children=phalanges)
fingers_list.append(finger)

# Initialize an empty list to hold the fingers_list
fingers_assemble = Pos(0, palm_height, 0)*Rot(Z=90)*Rot(X=-90)*Compound(label="fingers", children=fingers_list)

hand = Compound(label="hand", children=[palm_collection, fingers_assemble])
print(hand.location)
show(hand)
c = hand.location*(Rectangle(10, 10))

# Assuming the tree is already created and named 'hand', similar to your structure

def save_stl(node, parent_location=None):
    # If there's a parent location, apply its transformation to the current node
    if parent_location is not None:
        current_location = parent_location * node.location
    else:
        current_location = node.location
    
    if not node.children:
        # Before saving the STL, ensure the node's location is updated with the cumulative transformation
        # Assuming there's a method to temporarily set the location for export purposes
        original_location = node.location
        node.location = current_location
        node.export_stl(f"hand/{node.parent.label}-{node.label}.stl")
        # Restore the original location if necessary
        node.location = original_location
    else:
        for child in node.children:
            # Pass the current (possibly transformed) location to children as their parent location
            save_stl(child, current_location)

# Uncomment the following line to save a single stl
#hand.export_stl("hand.stl")

# Uncomment the following line to save the STL files tree
#save_stl(hand)



# %%
