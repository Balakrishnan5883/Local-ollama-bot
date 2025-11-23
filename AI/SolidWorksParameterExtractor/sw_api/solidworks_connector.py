import win32com.client
import pythoncom


class SolidWorksConnector:
    def __init__(self):
        self.app = self._connect_to_solidworks()
        self.doc = self.app.ActiveDoc if self.app else None

    def _connect_to_solidworks(self):
        try:
            pythoncom.CoInitialize()
            return win32com.client.Dispatch("SldWorks.Application")
        except Exception as e:
            print(f"Error connecting to SolidWorks: {e}")
            return None

    def is_connected(self):
        return self.app is not None

    def get_active_document_path(self):
        if self.doc:
            return self.doc.GetPathName()
        return "No active document"

    def get_dimensions(self):
        if not self.doc:
            return []

        try:
            dim_mgr = self.doc.Extension.get_Item("DimensionManager")
            dim_count = dim_mgr.GetCount()
            return [dim_mgr.get_Item(i).Name for i in range(dim_count)]
        except Exception as e:
            print(f"Error getting dimensions: {e}")
            return []

    def get_features(self):
        if not self.doc:
            return []

        try:
            feat_mgr = self.doc.FeatureManager
            feat_count = feat_mgr.GetFeatureCount()
            features = []n            for i in range(feat_count):
                feature = feat_mgr.GetFeature(i)
                features.append({
                    "name": feature.Name,
                    "type": feature.GetTypeName()
                })
            return features
        except Exception as e:
            print(f"Error getting features: {e}")
            return []

    def get_components(self):
        if not self.doc or not self.doc.GetType() == 2:  # 2 = swDocASSEMBLY
            return []

        try:
            comp_count = self.doc.GetComponents(False).Count
            components = []
            for i in range(comp_count):
                comp = self.doc.GetComponents(False).Item(i)
                components.append({
                    "name": comp.Name,
                    "path": comp.GetPathName()
                })
            return components
        except Exception as e:
            print(f"Error getting components: {e}")
            return []