# Rabbit Character V1 Action QA

**Gates:** `G2 PUPPET BUILD = PASS` · `G3 CORE ACTIONS = PASS` · `G4 VISUAL QA = PASS`

## Actions

| Action | Result |
|---|---|
| Idle | PASS / loopable 90f |
| HeadTilt | PASS / readable |
| HeadShake | PASS / readable |
| EarWiggle | PASS / rabbit-specific secondary motion |
| Bounce | PASS / readable |
| CarrotHappy | PASS / carrot and arm modules remain coordinated |
| Blink | PARTIAL / documented fallback; no eyelid component |

Evidence:

- `review/character_v1/rabbit_actions_contact_sheet.png`
- `05_animations/component_puppet_v1/rabbit_character_v1_preview.mp4`
- `05_animations/component_puppet_v1/rabbit_character_v1_preview_contact_sheet.png`

The source Material.001 and three PBR images remain on every action render. No traditional humanoid rig, smooth full-body skinning, UV rebuild, texture rebuild or PBR bake was introduced.

## Human review

The six required actions are readable in the provided contact sheet. The accepted limitation is Blink only; it does not block Rabbit V1.
