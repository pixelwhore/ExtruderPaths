import Rhino
import scriptcontext

class ContourObject():
    
    def __init__(self, geo, v_spacing, h_spacing):
        
        #set vertical spacing
        try:
            self.vertical_spacing = float(v_spacing)
        except:
            print("Vertical spacing value not castable to float")
            self.vertical_spacing = Rhino.Input.RhinoGet.GetNumber("Please input vertical spacing.", False, 0.5)[1]
        
        #set horizontal spacing           
        try:
            self.horizontal_spacing = float(h_spacing)
        except:
            print("Horizontal spacing value not castable to float")
            self.horizontal_spacing = Rhino.Input.RhinoGet.GetNumber("Please input horizontal spacing.", False, 0.5)[1]
                    
        #set geometry
        self.initial_geo = None
        if geo.GetType() == Rhino.Geometry.Brep:
            self.initial_geo = geo
        else:
            try:
                self.initial_geo = geo.Brep()
            except:
                print("Base geometry is not a Brep")              
            
        self.tool_path = self._contour()
        
        scriptcontext.doc.Objects.AddCurve(self.tool_path)
        
    def _contour(self):
        crvs = Rhino.Geometry.Brep.CreateContourCurves(self.initial_geo, Rhino.Geometry.Point3d(0, 0, 0), Rhino.Geometry.Point3d(0, 0, 10000), self.vertical_spacing)
        new_curves = []
        new_trans = []
        for curve in crvs:
            new_curves.append(curve.Trim(curve.LengthParameter(self.horizontal_spacing)[1], curve.Domain.Max))
        for i in xrange(0,len(new_curves)-1):
            new_trans.append(Rhino.Geometry.Line(new_curves[i].PointAtEnd, new_curves[i+1].PointAtStart).ToNurbsCurve())
        return Rhino.Geometry.Curve.JoinCurves(new_curves + new_trans)[0]

if __name__=="__main__":
    test, base_geo = Rhino.Input.RhinoGet.GetOneObject("Select geo to generate paths", False, None)
    if test == Rhino.Commands.Result.Success:
        contour_geo = ContourObject(base_geo.Brep(), 0.5, 0.5)
    else:
        print("Selection failed...")       