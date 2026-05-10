"""
main.py  –  PackManager: KivyMD + MongoDB Atlas packaging CRUD app
Targets KivyMD 1.1.1 / Kivy 2.3.0 (Android-compatible)
"""

from kivy.lang import Builder
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.properties import StringProperty, ObjectProperty
from kivy.uix.boxlayout import BoxLayout

from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.list import (
    MDList,
    TwoLineIconListItem,
    IconLeftWidget,
)
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from database import Database

# ─────────────────────────────────────────────────────────────────────────────
# KV UI Definition
# ─────────────────────────────────────────────────────────────────────────────
KV = """
#:import dp kivy.metrics.dp

# ── Root Layout ──────────────────────────────────────────────────────────────
MDBoxLayout:
    orientation: 'vertical'
    md_bg_color: app.theme_cls.bg_normal

    MDTopAppBar:
        title: "  PackManager"
        left_action_items: [["package-variant", lambda x: None]]
        elevation: 4
        md_bg_color: app.theme_cls.primary_color

    MDBottomNavigation:
        id: bottom_nav
        selected_color_background: app.theme_cls.primary_dark
        text_color_active: 1, 1, 1, 1
        on_switch_tabs: app.on_tab_switched(*args)

        MDBottomNavigationItem:
            name: 'search'
            text: 'Search'
            icon: 'magnify'
            SearchPanel:
                id: search_panel

        MDBottomNavigationItem:
            name: 'inventory'
            text: 'Inventory'
            icon: 'format-list-bulleted'
            InventoryPanel:
                id: inventory_panel

        MDBottomNavigationItem:
            name: 'add_item'
            text: 'Add Item'
            icon: 'plus-box-outline'
            AddItemPanel:
                id: add_item_panel

        MDBottomNavigationItem:
            name: 'cartons'
            text: 'Cartons'
            icon: 'package-variant-closed'
            ManageCartonsPanel:
                id: cartons_panel


# ── Search Panel ─────────────────────────────────────────────────────────────
<SearchPanel>:
    orientation: 'vertical'
    padding: dp(16), dp(16), dp(16), dp(4)
    spacing: dp(10)
    md_bg_color: app.theme_cls.bg_normal

    MDCard:
        size_hint_y: None
        height: dp(72)
        padding: dp(8)
        elevation: 3
        radius: [dp(12)]

        MDBoxLayout:
            spacing: dp(8)

            MDIcon:
                icon: "magnify"
                size_hint_x: None
                width: dp(32)
                theme_text_color: "Primary"
                valign: "center"

            MDTextField:
                id: search_field
                hint_text: "Search item (e.g. Hammer, Box, Lamp...)"
                mode: "fill"
                fill_color: 0, 0, 0, 0
                line_color_focus: app.theme_cls.primary_color
                on_text: root.perform_search(self.text)

    MDBoxLayout:
        size_hint_y: None
        height: dp(28)
        spacing: dp(8)

        MDLabel:
            id: status_label
            text: "Type above to search your inventory"
            theme_text_color: "Hint"
            font_style: "Caption"

    MDScrollView:
        do_scroll_x: False
        MDList:
            id: results_list
            padding: 0


# ── Inventory Panel ───────────────────────────────────────────────────────────
<InventoryPanel>:
    orientation: 'vertical'
    md_bg_color: app.theme_cls.bg_normal

    MDBoxLayout:
        size_hint_y: None
        height: dp(52)
        padding: dp(16), dp(8), dp(16), dp(0)
        spacing: dp(8)

        MDIcon:
            icon: "format-list-bulleted"
            size_hint_x: None
            width: dp(24)
            theme_text_color: "Primary"

        MDLabel:
            id: inv_status
            text: "Loading inventory..."
            theme_text_color: "Secondary"
            font_style: "Subtitle2"

    MDScrollView:
        do_scroll_x: False
        MDList:
            id: inventory_list
            padding: 0


# ── Add Item Panel ────────────────────────────────────────────────────────────
<AddItemPanel>:
    orientation: 'vertical'
    padding: dp(24)
    spacing: dp(16)
    md_bg_color: app.theme_cls.bg_normal

    MDLabel:
        text: "Add New Item"
        font_style: "H5"
        theme_text_color: "Primary"
        size_hint_y: None
        height: dp(44)

    MDCard:
        orientation: 'vertical'
        padding: dp(20)
        spacing: dp(16)
        size_hint_y: None
        height: dp(280)
        elevation: 2
        radius: [dp(12)]

        MDTextField:
            id: item_name_field
            hint_text: "Item Name  (e.g. Blue Hammer)"
            mode: "rectangle"
            icon_right: "tag-outline"

        MDTextField:
            id: carton_id_field
            hint_text: "Carton ID  (tap to pick or type)"
            mode: "rectangle"
            icon_right: "chevron-down"
            on_focus: if self.focus: root.show_carton_menu(self)

        MDRaisedButton:
            id: add_btn
            text: "  ADD ITEM  "
            size_hint_x: 1
            height: dp(50)
            md_bg_color: app.theme_cls.primary_color
            _no_ripple_effect: False
            on_release: root.add_item()

    MDLabel:
        id: add_status
        text: ""
        theme_text_color: "Hint"
        font_style: "Caption"
        size_hint_y: None
        height: dp(20)

    Widget:


# ── Manage Cartons Panel ──────────────────────────────────────────────────────
<ManageCartonsPanel>:
    orientation: 'vertical'
    padding: dp(16)
    spacing: dp(12)
    md_bg_color: app.theme_cls.bg_normal

    MDLabel:
        text: "Manage Cartons"
        font_style: "H5"
        theme_text_color: "Primary"
        size_hint_y: None
        height: dp(44)

    MDCard:
        orientation: 'vertical'
        padding: dp(16)
        spacing: dp(12)
        size_hint_y: None
        height: dp(220)
        elevation: 2
        radius: [dp(12)]

        MDTextField:
            id: carton_id_input
            hint_text: "Carton ID  (e.g. BOX-01, ATTIC-A)"
            mode: "rectangle"
            icon_right: "identifier"

        MDTextField:
            id: location_input
            hint_text: "Location  (e.g. Garage Shelf B)"
            mode: "rectangle"
            icon_right: "map-marker-outline"

        MDRaisedButton:
            text: "  SAVE CARTON  "
            size_hint_x: 1
            height: dp(50)
            md_bg_color: app.theme_cls.primary_color
            on_release: root.save_carton()

    MDLabel:
        id: carton_status
        text: ""
        theme_text_color: "Hint"
        font_style: "Caption"
        size_hint_y: None
        height: dp(20)

    MDBoxLayout:
        size_hint_y: None
        height: dp(32)
        padding: dp(4), dp(4), 0, 0

        MDIcon:
            icon: "package-variant"
            size_hint_x: None
            width: dp(24)
            theme_text_color: "Secondary"

        MDLabel:
            id: carton_list_label
            text: "  Saved Cartons"
            font_style: "Subtitle2"
            theme_text_color: "Secondary"

    MDScrollView:
        do_scroll_x: False
        MDList:
            id: cartons_list
            padding: 0


# ── Edit Item Dialog Content ──────────────────────────────────────────────────
<ItemEditContent>:
    orientation: 'vertical'
    spacing: dp(12)
    size_hint_y: None
    height: dp(160)

    MDTextField:
        id: edit_item_name
        hint_text: "Item Name"
        mode: "rectangle"

    MDTextField:
        id: edit_carton_id
        hint_text: "Carton ID"
        mode: "rectangle"
        icon_right: "chevron-down"
        on_focus: if self.focus: root.show_carton_menu(self)


# ── Edit Carton Dialog Content ────────────────────────────────────────────────
<CartonEditContent>:
    orientation: 'vertical'
    spacing: dp(12)
    size_hint_y: None
    height: dp(80)

    MDTextField:
        id: edit_location
        hint_text: "New Location"
        mode: "rectangle"
        icon_right: "map-marker-outline"
"""


# ─────────────────────────────────────────────────────────────────────────────
# Dialog Content Widgets
# ─────────────────────────────────────────────────────────────────────────────

class ItemEditContent(MDBoxLayout):
    """Content widget for the Edit Item dialog."""

    def show_carton_menu(self, field):
        """Populate carton dropdown in the edit dialog."""
        db = Database.get()
        if not db.is_connected():
            return

        def on_cartons(cartons, error):
            if error or not cartons:
                return

            def build_menu(dt):
                items = [
                    {
                        "text": f"{c['carton_id']}  ({c['location']})",
                        "viewclass": "OneLineListItem",
                        "on_release": lambda c_id=c["carton_id"]: _pick(c_id),
                    }
                    for c in cartons
                ]

                def _pick(cid):
                    field.text = cid
                    if hasattr(self, "_menu") and self._menu:
                        self._menu.dismiss()

                self._menu = MDDropdownMenu(
                    caller=field,
                    items=items,
                    width_mult=4,
                    max_height=dp(200),
                )
                self._menu.open()

            Clock.schedule_once(build_menu)

        db.get_all_cartons(on_cartons)


class CartonEditContent(MDBoxLayout):
    """Content widget for the Edit Carton dialog."""
    pass


# ─────────────────────────────────────────────────────────────────────────────
# Screen Panels
# ─────────────────────────────────────────────────────────────────────────────

class SearchPanel(MDBoxLayout):
    """Tab 1 – live fuzzy search with joined carton + location display."""

    _search_event = None  # debounce timer

    def perform_search(self, text: str):
        # Debounce: wait 350 ms after last keystroke
        if self._search_event:
            self._search_event.cancel()
        self._search_event = Clock.schedule_once(
            lambda dt: self._do_search(text), 0.35
        )

    def _do_search(self, text: str):
        db = Database.get()
        if not db.is_connected():
            self.ids.status_label.text = "⚠  Not connected to database"
            return

        text = text.strip()
        if not text:
            self.ids.status_label.text = "Type above to search your inventory"
            self.ids.results_list.clear_widgets()
            return

        self.ids.status_label.text = "Searching…"

        def on_results(results, error):
            def update(dt):
                lst = self.ids.results_list
                lst.clear_widgets()
                if error:
                    self.ids.status_label.text = f"Error: {error}"
                    return
                count = len(results)
                self.ids.status_label.text = (
                    f"{count} result{'s' if count != 1 else ''} found"
                    if count else "No items match that search"
                )
                for r in results:
                    row = TwoLineIconListItem(
                        text=r["item_name"],
                        secondary_text=(
                            f"Carton: {r['carton_id']}   "
                            f"|   Location: {r['location']}"
                        ),
                    )
                    icon = IconLeftWidget(icon="package-variant")
                    row.add_widget(icon)
                    lst.add_widget(row)

            Clock.schedule_once(update)

        db.search_items(text, on_results)


class InventoryPanel(MDBoxLayout):
    """Tab 2 – full scrollable inventory list with Edit / Delete."""

    _edit_dialog = None
    _edit_item_id = None

    def refresh(self):
        db = Database.get()
        if not db.is_connected():
            Clock.schedule_once(
                lambda dt: setattr(
                    self.ids.inv_status, "text",
                    "⚠  Not connected to database"
                )
            )
            return

        def on_items(items, error):
            def update(dt):
                lst = self.ids.inventory_list
                lst.clear_widgets()
                if error:
                    self.ids.inv_status.text = f"Error: {error}"
                    return
                count = len(items)
                self.ids.inv_status.text = (
                    f"{count} item{'s' if count != 1 else ''} in inventory"
                )
                for item in items:
                    self._add_row(lst, item)

            Clock.schedule_once(update)

        db.get_all_items(on_items)

    def _add_row(self, lst, item):
        row = TwoLineIconListItem(
            text=item["item_name"],
            secondary_text=(
                f"Carton: {item['carton_id']}   |   Location: {item['location']}"
            ),
        )
        icon = IconLeftWidget(icon="package")
        row.add_widget(icon)

        # Store refs for actions
        row._item_id = str(item["_id"])
        row._item_name = item["item_name"]
        row._carton_id = item["carton_id"]
        row.bind(on_release=lambda x: self._open_edit(x))
        lst.add_widget(row)

    def _open_edit(self, row):
        content = ItemEditContent()
        content.ids.edit_item_name.text = row._item_name
        content.ids.edit_carton_id.text = row._carton_id
        self._edit_item_id = row._item_id

        self._edit_dialog = MDDialog(
            title="Edit Item",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(
                    text="DELETE",
                    theme_text_color="Custom",
                    text_color=(0.9, 0.2, 0.2, 1),
                    on_release=lambda x: self._delete_item(),
                ),
                MDFlatButton(
                    text="CANCEL",
                    on_release=lambda x: self._edit_dialog.dismiss(),
                ),
                MDRaisedButton(
                    text="SAVE",
                    on_release=lambda x: self._save_edit(content),
                ),
            ],
        )
        self._edit_dialog.open()

    def _save_edit(self, content):
        name = content.ids.edit_item_name.text.strip()
        cid = content.ids.edit_carton_id.text.strip()
        if not name or not cid:
            PackagingApp.snack("Item name and Carton ID cannot be empty")
            return

        db = Database.get()
        item_id = self._edit_item_id
        self._edit_dialog.dismiss()

        def cb(ok, err):
            def update(dt):
                if err:
                    PackagingApp.snack(f"Error: {err}")
                else:
                    PackagingApp.snack("Item updated ✓")
                    self.refresh()

            Clock.schedule_once(update)

        db.update_item(item_id, name, cid, cb)

    def _delete_item(self):
        db = Database.get()
        item_id = self._edit_item_id
        self._edit_dialog.dismiss()

        def cb(ok, err):
            def update(dt):
                if err:
                    PackagingApp.snack(f"Error: {err}")
                else:
                    PackagingApp.snack("Item deleted")
                    self.refresh()

            Clock.schedule_once(update)

        db.delete_item(item_id, cb)


class AddItemPanel(MDBoxLayout):
    """Tab 3 – form to add a new item with carton selector."""

    _carton_menu = None

    def show_carton_menu(self, field):
        db = Database.get()
        if not db.is_connected():
            PackagingApp.snack("Not connected to database")
            return

        def on_cartons(cartons, error):
            def build(dt):
                if error or not cartons:
                    PackagingApp.snack(
                        "No cartons found – add one in the Cartons tab first"
                    )
                    return

                def _pick(cid):
                    field.text = cid
                    if self._carton_menu:
                        self._carton_menu.dismiss()

                menu_items = [
                    {
                        "text": f"{c['carton_id']}  —  {c['location']}",
                        "viewclass": "OneLineListItem",
                        "on_release": (
                            lambda cid=c["carton_id"]: _pick(cid)
                        ),
                    }
                    for c in cartons
                ]

                self._carton_menu = MDDropdownMenu(
                    caller=field,
                    items=menu_items,
                    width_mult=5,
                    max_height=dp(240),
                )
                self._carton_menu.open()

            Clock.schedule_once(build)

        db.get_all_cartons(on_cartons)

    def add_item(self):
        name = self.ids.item_name_field.text.strip()
        cid = self.ids.carton_id_field.text.strip()

        if not name:
            self.ids.add_status.text = "⚠  Item name is required"
            return
        if not cid:
            self.ids.add_status.text = "⚠  Carton ID is required"
            return

        db = Database.get()
        if not db.is_connected():
            self.ids.add_status.text = "⚠  Not connected to database"
            return

        self.ids.add_btn.text = "SAVING…"
        self.ids.add_btn.disabled = True

        def cb(inserted_id, error):
            def update(dt):
                self.ids.add_btn.text = "  ADD ITEM  "
                self.ids.add_btn.disabled = False
                if error:
                    self.ids.add_status.text = f"Error: {error}"
                    PackagingApp.snack(f"Failed: {error}")
                else:
                    self.ids.add_status.text = f"✓  '{name}' added to {cid}"
                    self.ids.item_name_field.text = ""
                    self.ids.carton_id_field.text = ""
                    PackagingApp.snack(f"'{name}' added successfully ✓")

            Clock.schedule_once(update)

        db.add_item(name, cid, cb)


class ManageCartonsPanel(MDBoxLayout):
    """Tab 4 – add / edit / delete cartons and their locations."""

    _edit_dialog = None
    _editing_carton_id = None

    def refresh(self):
        db = Database.get()
        if not db.is_connected():
            Clock.schedule_once(
                lambda dt: setattr(
                    self.ids.carton_list_label, "text",
                    "  ⚠  Not connected"
                )
            )
            return

        def on_cartons(cartons, error):
            def update(dt):
                lst = self.ids.cartons_list
                lst.clear_widgets()
                if error:
                    self.ids.carton_list_label.text = f"  Error: {error}"
                    return
                count = len(cartons)
                self.ids.carton_list_label.text = (
                    f"  Saved Cartons  ({count})"
                )
                for c in cartons:
                    self._add_row(lst, c)

            Clock.schedule_once(update)

        db.get_all_cartons(on_cartons)

    def _add_row(self, lst, carton):
        row = TwoLineIconListItem(
            text=carton["carton_id"],
            secondary_text=f"Location: {carton['location']}",
        )
        icon = IconLeftWidget(icon="package-variant-closed")
        row.add_widget(icon)
        row._carton_id = carton["carton_id"]
        row._location = carton["location"]
        row.bind(on_release=lambda x: self._open_edit(x))
        lst.add_widget(row)

    def save_carton(self):
        cid = self.ids.carton_id_input.text.strip()
        loc = self.ids.location_input.text.strip()

        if not cid:
            self.ids.carton_status.text = "⚠  Carton ID is required"
            return
        if not loc:
            self.ids.carton_status.text = "⚠  Location is required"
            return

        db = Database.get()
        if not db.is_connected():
            self.ids.carton_status.text = "⚠  Not connected"
            return

        def cb(result, error):
            def update(dt):
                if error:
                    self.ids.carton_status.text = f"⚠  {error}"
                    PackagingApp.snack(error)
                else:
                    self.ids.carton_status.text = f"✓  '{cid}' saved"
                    self.ids.carton_id_input.text = ""
                    self.ids.location_input.text = ""
                    PackagingApp.snack(f"Carton '{cid}' saved ✓")
                    self.refresh()

            Clock.schedule_once(update)

        db.add_carton(cid, loc, cb)

    def _open_edit(self, row):
        content = CartonEditContent()
        content.ids.edit_location.text = row._location
        self._editing_carton_id = row._carton_id

        self._edit_dialog = MDDialog(
            title=f"Edit: {row._carton_id}",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(
                    text="DELETE",
                    theme_text_color="Custom",
                    text_color=(0.9, 0.2, 0.2, 1),
                    on_release=lambda x: self._delete_carton(),
                ),
                MDFlatButton(
                    text="CANCEL",
                    on_release=lambda x: self._edit_dialog.dismiss(),
                ),
                MDRaisedButton(
                    text="UPDATE",
                    on_release=lambda x: self._update_carton(content),
                ),
            ],
        )
        self._edit_dialog.open()

    def _update_carton(self, content):
        new_loc = content.ids.edit_location.text.strip()
        if not new_loc:
            PackagingApp.snack("Location cannot be empty")
            return

        db = Database.get()
        cid = self._editing_carton_id
        self._edit_dialog.dismiss()

        def cb(ok, err):
            def update(dt):
                if err:
                    PackagingApp.snack(f"Error: {err}")
                else:
                    PackagingApp.snack(f"'{cid}' updated ✓")
                    self.refresh()

            Clock.schedule_once(update)

        db.update_carton(cid, new_loc, cb)

    def _delete_carton(self):
        db = Database.get()
        cid = self._editing_carton_id
        self._edit_dialog.dismiss()

        def cb(ok, err):
            def update(dt):
                if err:
                    PackagingApp.snack(f"Error: {err}")
                else:
                    PackagingApp.snack(
                        f"Carton '{cid}' and its items deleted"
                    )
                    self.refresh()

            Clock.schedule_once(update)

        db.delete_carton(cid, cb)


# ─────────────────────────────────────────────────────────────────────────────
# Main App
# ─────────────────────────────────────────────────────────────────────────────

class PackagingApp(MDApp):
    """
    Entry point.
    - Sets Material Design theme
    - Connects to MongoDB Atlas on startup
    - Manages tab switch events
    """

    # Class-level snackbar helper so panels can call it without app ref
    @staticmethod
    def snack(text: str, duration: float = 3.0):
        def _show(dt):
            Snackbar(text=text, snackbar_x="8dp", snackbar_y="8dp",
                     size_hint_x=0.97, duration=duration).open()
        Clock.schedule_once(_show)

    # ── App lifecycle ──────────────────────────────────────────────────────

    def build(self):
        self.theme_cls.theme_style = "Light"          # or "Dark"
        self.theme_cls.primary_palette = "DeepOrange"
        self.theme_cls.accent_palette = "Amber"
        self.title = "PackManager"
        return Builder.load_string(KV)

    def on_start(self):
        """Connect to Atlas and show connection status via Snackbar."""
        PackagingApp.snack("Connecting to database…", duration=3)

        db = Database.get()
        db.connect_async(
            on_success=self._on_db_connected,
            on_error=self._on_db_error,
        )

    def _on_db_connected(self):
        def update(dt):
            PackagingApp.snack("Connected to MongoDB Atlas ✓", duration=2)
            # Pre-load inventory and cartons
            inv = self.root.ids.inventory_panel
            inv.refresh()
            cartons = self.root.ids.cartons_panel
            cartons.refresh()

        Clock.schedule_once(update)

    def _on_db_error(self, error: str):
        def update(dt):
            PackagingApp.snack(
                f"DB Error: {error[:80]}", duration=6
            )

        Clock.schedule_once(update)

    # ── Tab switch ────────────────────────────────────────────────────────

    def on_tab_switched(self, *args):
        """
        KivyMD 1.1.1 on_switch_tabs passes variable number of args.
        We pick the tab name safely from whichever string arg matches.
        """
        item_name = None
        for a in args:
            if isinstance(a, str):
                item_name = a   # last/only string arg is the tab name
        if item_name == "inventory":
            self.root.ids.inventory_panel.refresh()
        elif item_name == "cartons":
            self.root.ids.cartons_panel.refresh()


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    PackagingApp().run()