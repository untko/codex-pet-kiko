# Kiko look mechanics

Kiko is a soft 3D gecko with a large separate head, flexible neck and tail, large physical eyeballs, small arms, and planted feet. The approved look family stays in Kiko's neutral green/turquoise palette with the cream belly and original warm brown-and-gold eyes.

## Natural motion

- Anchor both feet, the pelvis, and the lower torso to Kiko's neutral baseline. Keep overall body scale and volume constant.
- The complete eyeballs lead each gaze: sclera, iris, pupil, eyelids, rim, and highlights rotate/redraw together inside the original sockets. Do not slide isolated pupils or add replacement eyes.
- The snout and head follow with a restrained yaw or pitch; the flexible neck bends smoothly without stretching the skull or changing facial proportions.
- The upper torso follows only slightly. Arms remain naturally attached and relaxed. The tail counterbalances with a small continuous curve and never flips sides or teleports.
- Use even 22.5-degree steps. No adjacent pose may introduce a larger head turn, bend, scale shift, tail jump, or registration change than its neighbors.
- Do not rotate or tilt the whole sprite, move the feet, add props or effects, or change Kiko's identity.

## Cardinal pose families

- `000 up`: both eye globes aim clearly upward; eyelids expose the lower iris edge; the snout and chin lift slightly while the neck extends upward. The planted body remains front-readable and the tail stays low.
- `090 screen-right`: pupils, irises, and nose tip cross to screen-right of the head center; the head yaws right so the screen-left cheek and nearer eye remain more visible while the far side is modestly occluded. The neck follows right and the tail lags subtly left.
- `180 down`: both eye globes aim clearly downward; upper lids lower slightly; the snout and chin tuck toward the cream chest while the neck compresses gently. Feet and lower torso remain fixed.
- `270 screen-left`: pupils, irises, and nose tip cross to screen-left of the head center; the head yaws left so the screen-right cheek and nearer eye remain more visible while the far side is modestly occluded. The neck follows left and the tail lags subtly right.

Diagonals interpolate the adjacent cardinal families without reversing the clockwise loop. `157.5 -> 180` and `337.5 -> 000` must each be exactly one natural step, with continuous eyes, head, neck, torso, and tail.
