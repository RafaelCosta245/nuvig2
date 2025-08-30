import flet as ft
import uuid

def main(page: ft.Page):
    page.title = "Drag and Drop Table"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.update()

    # Lists to hold items in each column
    col1_items = []
    col2_items = []
    col3_items = []

    # Cycle through items: A to col1, B to col2, C to col3, repeat
    item_cycle = ["ITEM A", "ITEM B", "ITEM C"]
    cycle_index = 0

    def drag_will_accept(e):
        # Highlight the target column or item with a border
        e.control.content.border = ft.border.all(
            2, ft.Colors.BLACK45 if e.data == "true" else ft.Colors.RED
        )
        e.control.update()
        print(f"Drag will accept on control with data: {e.control.data}")

    def drag_accept(e: ft.DragTargetEvent):
        print(f"=== Drag accept called ===")
        src = page.get_control(e.src_id)
        print(f"Source control ID: {e.src_id}, Source data: {src.data}")
        print(f"Target control data: {e.control.data}")

        # Find and remove the source item
        item = None
        src_list = None
        if any(item.data == src.data for item in col1_items):
            item = next(item for item in col1_items if item.data == src.data)
            col1_items.remove(item)
            src_list = col1_items
            print(f"Removed item {src.data} from col1")
        elif any(item.data == src.data for item in col2_items):
            item = next(item for item in col2_items if item.data == src.data)
            col2_items.remove(item)
            src_list = col2_items
            print(f"Removed item {src.data} from col2")
        elif any(item.data == src.data for item in col3_items):
            item = next(item for item in col3_items if item.data == src.data)
            col3_items.remove(item)
            src_list = col3_items
            print(f"Removed item {src.data} from col3")

        if item:
            # Add to the target column
            target_col_data = e.control.data
            if target_col_data == "col1":
                col1_items.append(item)
                print(f"Added item {src.data} to col1")
            elif target_col_data == "col2":
                col2_items.append(item)
                print(f"Added item {src.data} to col2")
            elif target_col_data == "col3":
                col3_items.append(item)
                print(f"Added item {src.data} to col3")
            else:
                print("No matching column found for target")
                # If no valid target column, return item to source
                src_list.append(item)
            e.control.content.border = None  # Clear border
            e.control.update()
            update_columns()
        else:
            print(f"No item found for src_id: {e.src_id}")

    def drag_leave(e):
        e.control.content.border = None
        e.control.update()
        print(f"Drag left control with data: {e.control.data}")

    def add_item(e):
        nonlocal cycle_index
        item_label = item_cycle[cycle_index % 3]
        column_index = cycle_index % 3

        # Generate a unique ID for the item
        item_id = str(uuid.uuid4())

        # Create a draggable item
        item = ft.Draggable(
            group="items",
            content=ft.Container(
                content=ft.Text(item_label),
                bgcolor=ft.Colors.BLUE_100,
                padding=10,
                border_radius=5,
                data=item_id,
            ),
            data=item_id,
            content_feedback=ft.Container(
                width=20,
                height=20,
                bgcolor=ft.Colors.BLUE_100,
                border_radius=3,
            ),
        )

        # Add to the appropriate column
        if column_index == 0:
            col1_items.append(item)
            print(f"Added {item_label} to col1, ID: {item_id}")
        elif column_index == 1:
            col2_items.append(item)
            print(f"Added {item_label} to col2, ID: {item_id}")
        else:
            col3_items.append(item)
            print(f"Added {item_label} to col3, ID: {item_id}")

        cycle_index += 1
        update_columns()

    def update_columns():
        col1.content.controls = col1_items
        col2.content.controls = col2_items
        col3.content.controls = col3_items
        print("Updating columns:")
        print(f"col1_items: {[item.data for item in col1_items]}")
        print(f"col2_items: {[item.data for item in col2_items]}")
        print(f"col3_items: {[item.data for item in col3_items]}")
        page.update()

    # Columns as Containers wrapped in DragTarget
    col1 = ft.Container(
        content=ft.Column(spacing=10, expand=True),
        bgcolor=ft.Colors.GREY_200,
        padding=10,
        border_radius=5,
    )
    col2 = ft.Container(
        content=ft.Column(spacing=10, expand=True),
        bgcolor=ft.Colors.GREY_200,
        padding=10,
        border_radius=5,
    )
    col3 = ft.Container(
        content=ft.Column(spacing=10, expand=True),
        bgcolor=ft.Colors.GREY_200,
        padding=10,
        border_radius=5,
    )

    # Wrap columns in DragTarget
    col1_drag = ft.DragTarget(
        group="items",
        content=col1,
        on_will_accept=drag_will_accept,
        on_accept=drag_accept,
        on_leave=drag_leave,
        data="col1",
    )
    col2_drag = ft.DragTarget(
        group="items",
        content=col2,
        on_will_accept=drag_will_accept,
        on_accept=drag_accept,
        on_leave=drag_leave,
        data="col2",
    )
    col3_drag = ft.DragTarget(
        group="items",
        content=col3,
        on_will_accept=drag_will_accept,
        on_accept=drag_accept,
        on_leave=drag_leave,
        data="col3",
    )

    # Button to add item
    add_button = ft.ElevatedButton("Adicionar Item", on_click=add_item)

    # Layout
    row = ft.Row(
        [col1_drag, col2_drag, col3_drag],
        expand=True,
        spacing=20,
    )

    page.add(add_button, row)

ft.app(main)