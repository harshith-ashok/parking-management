import cv2
import json
import numpy as np
# Global variables
coords = []
current_slot = []
slot_name = ""
all_slots = []


def mouse_callback(event, x, y, flags, param):
    global current_slot, coords

    if event == cv2.EVENT_LBUTTONDOWN:
        coords.append([x, y])
        current_slot.append([x, y])
        print(f"Point added: ({x}, {y})")

        # Draw circle at clicked point
        cv2.circle(param, (x, y), 5, (0, 255, 0), -1)

        # If we have more than 1 point, draw lines
        if len(current_slot) > 1:
            cv2.polylines(param, [np.array(current_slot)],
                          False, (0, 255, 0), 2)

        cv2.imshow("Mark Parking Slots", param)


# Load image
image_path = "parking.jpg"
img = cv2.imread(image_path)

if img is None:
    print(f"Error: Could not load image '{image_path}'")
    exit()

img_copy = img.copy()

print("=" * 60)
print("PARKING SLOT COORDINATE MARKER")
print("=" * 60)
print("Instructions:")
print("1. Click 4 corners of a parking slot (top-left, top-right, bottom-right, bottom-left)")
print("2. Press 's' to save the slot and start a new one")
print("3. Press 'u' to undo last point")
print("4. Press 'r' to reset current slot")
print("5. Press 'q' when done (will save to slots.json)")
print("=" * 60)

cv2.namedWindow("Mark Parking Slots")
cv2.setMouseCallback("Mark Parking Slots", mouse_callback, img_copy)

while True:
    cv2.imshow("Mark Parking Slots", img_copy)
    key = cv2.waitKey(1) & 0xFF

    # Save current slot
    if key == ord('s'):
        if len(current_slot) == 4:
            slot_name = input("Enter slot ID (e.g., L1, R1): ")
            all_slots.append({
                "id": slot_name,
                "polygon": current_slot
            })
            print(f"Slot '{slot_name}' saved with coordinates: {current_slot}")

            # Draw final polygon
            cv2.polylines(
                img_copy, [np.array(current_slot)], True, (0, 255, 0), 2)
            cv2.putText(img_copy, slot_name,
                        (current_slot[0][0], current_slot[0][1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            current_slot = []
        else:
            print(
                f"Error: Need exactly 4 points, you have {len(current_slot)}")

    # Undo last point
    elif key == ord('u'):
        if current_slot:
            removed = current_slot.pop()
            coords.pop()
            print(f"Removed point: {removed}")
            img_copy = img.copy()

            # Redraw all saved slots
            for slot in all_slots:
                cv2.polylines(
                    img_copy, [np.array(slot['polygon'])], True, (0, 255, 0), 2)
                cv2.putText(img_copy, slot['id'],
                            (slot['polygon'][0][0],
                             slot['polygon'][0][1] - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            # Redraw current slot
            for point in current_slot:
                cv2.circle(img_copy, tuple(point), 5, (0, 255, 0), -1)
            if len(current_slot) > 1:
                cv2.polylines(
                    img_copy, [np.array(current_slot)], False, (0, 255, 0), 2)

    # Reset current slot
    elif key == ord('r'):
        current_slot = []
        img_copy = img.copy()

        # Redraw all saved slots
        for slot in all_slots:
            cv2.polylines(
                img_copy, [np.array(slot['polygon'])], True, (0, 255, 0), 2)
            cv2.putText(img_copy, slot['id'],
                        (slot['polygon'][0][0], slot['polygon'][0][1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        print("Current slot reset")

    # Quit and save
    elif key == ord('q'):
        break

# Save to JSON
if all_slots:
    output = {"slots": all_slots}
    with open("slots.json", "w") as f:
        json.dump(output, f, indent=2)
    print(f"\n✅ Saved {len(all_slots)} slots to slots.json")
    print("\nGenerated slots.json content:")
    print(json.dumps(output, indent=2))
else:
    print("\n❌ No slots marked")

cv2.destroyAllWindows()
