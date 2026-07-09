---
name: Tactile Pulse
colors:
  surface: '#0b1326'
  surface-dim: '#0b1326'
  surface-bright: '#31394d'
  surface-container-lowest: '#060e20'
  surface-container-low: '#131b2e'
  surface-container: '#171f33'
  surface-container-high: '#222a3d'
  surface-container-highest: '#2d3449'
  on-surface: '#dae2fd'
  on-surface-variant: '#ccc3d8'
  inverse-surface: '#dae2fd'
  inverse-on-surface: '#283044'
  outline: '#958da1'
  outline-variant: '#4a4455'
  surface-tint: '#d2bbff'
  primary: '#d2bbff'
  on-primary: '#3f008e'
  primary-container: '#7c3aed'
  on-primary-container: '#ede0ff'
  inverse-primary: '#732ee4'
  secondary: '#4cd7f6'
  on-secondary: '#003640'
  secondary-container: '#03b5d3'
  on-secondary-container: '#00424e'
  tertiary: '#ffb784'
  on-tertiary: '#4f2500'
  tertiary-container: '#a15100'
  on-tertiary-container: '#ffe0cd'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#eaddff'
  primary-fixed-dim: '#d2bbff'
  on-primary-fixed: '#25005a'
  on-primary-fixed-variant: '#5a00c6'
  secondary-fixed: '#acedff'
  secondary-fixed-dim: '#4cd7f6'
  on-secondary-fixed: '#001f26'
  on-secondary-fixed-variant: '#004e5c'
  tertiary-fixed: '#ffdcc6'
  tertiary-fixed-dim: '#ffb784'
  on-tertiary-fixed: '#301400'
  on-tertiary-fixed-variant: '#713700'
  background: '#0b1326'
  on-background: '#dae2fd'
  surface-variant: '#2d3449'
typography:
  display-lg:
    fontFamily: Hanken Grotesk
    fontSize: 48px
    fontWeight: '800'
    lineHeight: 56px
    letterSpacing: -0.02em
  display-lg-mobile:
    fontFamily: Hanken Grotesk
    fontSize: 36px
    fontWeight: '800'
    lineHeight: 42px
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Hanken Grotesk
    fontSize: 24px
    fontWeight: '700'
    lineHeight: 32px
  body-lg:
    fontFamily: Hanken Grotesk
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Hanken Grotesk
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  label-bold:
    fontFamily: JetBrains Mono
    fontSize: 14px
    fontWeight: '700'
    lineHeight: 20px
    letterSpacing: 0.05em
  button-text:
    fontFamily: Hanken Grotesk
    fontSize: 18px
    fontWeight: '700'
    lineHeight: 24px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  unit: 4px
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 40px
  gutter: 16px
  margin-mobile: 16px
  margin-desktop: 32px
---

## Brand & Style

This design system is engineered for immediate action and high-frequency engagement. The brand personality is **Reliable, Fast, and Intimate**, focusing on the "Buzz" of real-time activity. 

The visual style merges **Neumorphism** with **Glassmorphism** to create a "Soft-Tech" aesthetic. Elements should feel physically clickable and rooted in a three-dimensional space, using soft shadows for depth and frosted glass layers for information hierarchy. The interface avoids the coldness of traditional SaaS by using organic, tactile metaphors that make digital interactions feel rhythmic and responsive. Use vibrant blurs behind translucent surfaces to maintain a sense of energy without causing visual fatigue.

## Colors

The palette is anchored in a deep **Dark Mode** foundation to allow the high-vibrancy primary colors to "pop" as sources of light. 

- **Primary (Electric Purple):** Used for critical actions, active states, and "the buzz." It represents energy and urgency.
- **Secondary (Cyan Blue):** Used for secondary interactions, status indicators, and success states. It provides a cooling balance to the purple.
- **Neutral:** A deep slate-navy used for background surfaces. Pure black is avoided to maintain the soft, tactile shadows required for Neumorphism.
- **Alerts:** High-contrast Magenta (#F0ABFC) for urgent notifications that must bypass the standard hierarchy.

## Typography

The typography system utilizes **Hanken Grotesk** for its sharp, contemporary feel and excellent legibility in high-stress scenarios. **JetBrains Mono** is introduced for labels and technical status indicators to reinforce the "precision tool" aspect of the app.

Headlines should use extra-bold weights to command attention immediately. Body text remains clean with generous line height to ensure readability during fast-paced scrolling. All uppercase styles should be reserved for `label-bold` roles to differentiate meta-data from interactive content.

## Layout & Spacing

This design system employs a **Fluid Grid** with a strictly enforced 4px baseline shift. 

- **Mobile:** A 4-column grid with 16px margins. Elements are primarily full-width to maximize the hit area for tactile buttons.
- **Desktop:** A 12-column grid centered in a max-width container of 1280px. 
- **Spacing Philosophy:** Use "Intelligent Padding"—larger internal padding (24px+) for interactive cards to create the soft, pillowy look required for Neumorphism. Gutters remain tight (16px) to keep the data density high and the "speed" of the app apparent.

## Elevation & Depth

Hierarchy is established through **Tactile Layering**:

1.  **The Base:** A deep navy matte surface.
2.  **Neumorphic Raised:** Elements that sit "above" the surface using two shadows: a dark shadow (top-left) and a slightly lighter, tinted glow (bottom-right) to simulate a physical extrusion.
3.  **Glassmorphic Floating:** Modals and high-priority alerts float above all else with a `backdrop-filter: blur(20px)` and a thin 1px white border at 10% opacity.
4.  **Pressed State:** Buttons should visually "sink" into the interface when tapped, reversing the shadow direction to an internal `inset` shadow.

## Shapes

The shape language is dominated by **Soft Geometry**. 

Standard containers and cards use a 16px radius (`rounded-lg`). Buttons that represent the primary "Buzz" action are fully rounded (pill-shaped) to invite physical interaction. Use consistent corner smoothing (60%+) where possible to avoid the "robotic" look of standard CSS radii, leaning into a more organic, industrial design feel.

## Components

### Buttons & Interaction
- **Primary Pulse Button:** Large, circular or pill-shaped. Features a continuous "ripple" animation (low opacity rings expanding outward) to indicate an active state. 
- **Tactile Feedback:** On hover, the Neumorphic extrusion increases. On press, the element uses an inset shadow to appear physically depressed.

### Status Indicators
- **The "Buzz" Indicator:** A high-contrast dot (Electric Purple) with a subtle blur glow (`box-shadow: 0 0 12px primary`).
- **Activity Feed:** List items use glassmorphism with a subtle left-accent border color-coded to the priority level.

### Input Fields
- **Inset Wells:** Fields should look like they are carved into the UI. Use internal shadows rather than borders. The cursor and focus state should utilize the Cyan Blue for high visibility.

### Alerts
- **High-Contrast Overlays:** Urgent alerts bypass the dark theme with a semi-transparent Magenta background and heavy backdrop blur. Use high-weight typography for the headline.

### Cards
- **Soft-Containers:** Use a combination of a 1px border (color: neutral-700) and a soft ambient shadow. Backgrounds should be slightly lighter than the base surface (#1E293B).