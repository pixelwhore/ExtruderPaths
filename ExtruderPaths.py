import Rhino
import scriptcontext
import math
import System.Drawing


class ContourObject():
    
    def __init__(self, geo, v_spacing, h_spacing, ref_angle):
        
        self.initial_geo = geo
        self.vertical_spacing = float(v_spacing)
        self.horizontal_spacing = float(h_spacing)
        self.refpath_angle = float(ref_angle)
        
        self.toolpath = None
        self.refpath = None
        
    def Contour(self):
        crvs = Rhino.Geometry.Brep.CreateContourCurves(self.initial_geo, Rhino.Geometry.Point3d(0, 0, 0), Rhino.Geometry.Point3d(0, 0, 10000), self.vertical_spacing)
        tp = []
        tp_trans = []
        rp = []
        rp_trans = []
        
        for curve in crvs:
            tp.append(curve.Trim(curve.LengthParameter(self.horizontal_spacing)[1], curve.Domain.Max))
            rp.append(tp[-1].Offset(Rhino.Geometry.Plane.WorldXY, math.tan(math.radians(self.refpath_angle)) * 1, .050, 0)[0])
            rp[-1].Translate(0, 0, 1)
            
        for i in xrange(0,len(tp)-1):
            tp_trans.append(Rhino.Geometry.Line(tp[i].PointAtEnd, tp[i+1].PointAtStart).ToNurbsCurve())
            rp_trans.append(Rhino.Geometry.Line(rp[i].PointAtEnd, rp[i+1].PointAtStart).ToNurbsCurve())
            
        self.toolpath = Rhino.Geometry.Curve.JoinCurves(tp + tp_trans)[0]
        self.refpath = Rhino.Geometry.Curve.JoinCurves(rp + rp_trans)[0]
        
    def Bake(self):
        
        if self.toolpath:
            attr = GenerateAttributes("Tool Path", System.Drawing.Color.Red)
            scriptcontext.doc.Objects.AddCurve(self.toolpath, attr)
        
        if self.refpath:
            attr = GenerateAttributes("Reference Path", System.Drawing.Color.Chartreuse)
            scriptcontext.doc.Objects.AddCurve(self.refpath, attr)

def GenerateAttributes(layer_name, color):
    layer = Rhino.DocObjects.Layer()
    layer.Name = layer_name
    layer.Color = color 
    layer = scriptcontext.doc.Layers.Add(layer)
    
    attribute = Rhino.DocObjects.ObjectAttributes()
    attribute.LayerIndex = scriptcontext.doc.Layers.Find(layer_name, True)
    
    return attribute


if __name__=="__main__":
    if scriptcontext.doc.ModelUnitSystem != Rhino.UnitSystem.Millimeters:
        scriptcontext.doc.AdjustModelUnitSystem(Rhino.UnitSystem.Millimeters, True)
    
    get = Rhino.Input.Custom.GetObject()
    get.SetCommandPrompt("Select geometry to generate toolpaths")
    
    vert = Rhino.Input.Custom.OptionDouble(0.25, 0.10, 1.00)
    tran = Rhino.Input.Custom.OptionDouble(0.25, 0.10, 1.00)
    refc = Rhino.Input.Custom.OptionDouble(15.0, 0.0, 90.0)
    
    get.AddOptionDouble("Vertical_spacing", vert)
    get.AddOptionDouble("Transition_length", tran)
    get.AddOptionDouble("Reference_angle", refc)
    
    while True:
        result = get.Get()
        if result==Rhino.Input.GetResult.Option:
            continue
        break
    
    contour_geo = ContourObject(get.Object(0).Brep(), vert.CurrentValue, tran.CurrentValue, refc.CurrentValue)
    contour_geo.Contour()
    contour_geo.Bake()