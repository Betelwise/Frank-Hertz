from manim import *
import numpy as np

class FrankHertzMain(Scene):
    def construct(self):
        # Step 1: Create the Housing (Vacuum Tube)
        housing = RoundedRectangle(height=3, width=8, corner_radius=1, color=WHITE)
        
        # Step 2: Create the Cathode as a Parallelogram
        cathode = Polygon(
            LEFT * 3 + UP * 0.5,
            LEFT * 3 + DOWN * 0.5,
            LEFT * 2.5 + DOWN * 0.2,
            LEFT * 2.5 + UP * 0.8,
            color=RED
        )
        cathode.set_fill(RED, opacity=1)

        # Define attachment points for the spring (filament)
        bottom_attachment = LEFT * 3.5 + UP * -0.5     # where the filament attaches at the cathode
        top_attachment    = LEFT * 3.5 + UP * 0.5     # where.5 it attaches at the to.5p

        # Create the vertical spring:
        # - t runs from 0 to 1 (vertical progression)
        # - x = 0.1*sin(10*t) gives horizontal oscillation (i.e. the spring's wiggle)
        spring = ParametricFunction(
            lambda t: np.array([
                0.2 * np.sin(25 * t),  # x oscillation
                t,                     # y increases steadily from 0 to 1
                0
            ]),
            t_range=[0, 1],
            color=ORANGE
        )
        # Scale the spring vertically to match the desired height
        spring.scale(top_attachment[1] - bottom_attachment[1])
        # Move the spring so its bottom aligns with the bottom_attachment point
        spring.move_to(bottom_attachment, aligned_edge=DOWN)

        # Create the horizontal wires (extending from the endpoints)
        left_wire = Line(bottom_attachment + LEFT * 1, bottom_attachment, color=ORANGE).set_stroke(width=5)
        right_wire = Line(top_attachment, top_attachment + LEFT * 1, color=ORANGE).set_stroke(width=5)

        # Group the wires and spring together as the filament
        filament = VGroup(left_wire, spring, right_wire)
        
        # Step 2: Create the Anode and Collector
        anode = self.create_grid().move_to(ORIGIN)
        collector = cathode.copy().set_color(GREEN).move_to(RIGHT * 3)
        
        # Step 3: Create the Knob (Voltage Control)
        knob = Circle(radius=0.3, color=YELLOW).move_to(UP * 2)
        knob_label = Text("Voltage", font_size=24).next_to(knob, UP)
        

        # Animation Sequence 1: Housing, Cathode, and Filament Appear
        # self.play(Create(cathode), Create(filament), Create(housing))
        self.play(Create(housing))
        self.play(Create(cathode))
        self.play(Create(filament))
        # self.play(FadeIn(cathode), FadeIn(filament))
        # self.wait(1


        # Animation Sequence 2: Filament Heats Up
        glowing_filament = filament.copy().set_color(YELLOW)
        self.play(Transform(filament, glowing_filament), run_time=1)
        self.wait(1)

        # Step 3: Create Stationary Electrons (Wiggling Effect)
        stationary_electrons = VGroup()
        num_stationary = 10

        for i in range(num_stationary):
            # Random positions near the cathode
            position = LEFT * 3 + np.random.uniform(-0.5, 0.6) * UP + np.random.uniform(0, 0.3) * RIGHT
            electron = self.create_electronSimple(position)
            stationary_electrons.add(electron)

        self.play(FadeIn(stationary_electrons))
        
        # Wiggling effect (random timing for each electron)
        for _ in range(5):  # More wiggles
            animations = []
            for electron in stationary_electrons:
                # Each electron gets a different random wiggle
                animations.append(self.wiggle_electron(electron).set_run_time(0.2).set_start_time(np.random.uniform(0, 0.2)))

            self.play(AnimationGroup(*animations, lag_ratio=0.1))
        # Vanish stationary electrons
        self.play(FadeOut(stationary_electrons))
        self.wait(2)

        #create the anode and collector
        self.play(Create(anode), Create(collector))
        self.wait(1)

        # Create a ValueTracker to control the speed (voltage)
        voltage = ValueTracker(0.2)  # Change this value to speed up or slow down electrons
        # Define key positions along the electron path:
        # self.cathode_pos = LEFT * 3.2
        self.cathode_center = LEFT * 3.2
        self.anode_pos = ORIGIN
        self.collector_pos = RIGHT * 3
        # Step 6: Create Electrons One After Another
        electrons = VGroup()
        num_electrons = 10

        for i in range(num_electrons):
            electron = self.create_electron()
            electron.time_elapsed = 0
            electron.phase_offset = np.random.uniform(0, 5)  # Staggered start times

            # Store the starting position for the electron
            electron.start_pos = electron.get_center()

            electron.add_updater(lambda e, dt, volt=voltage: self.update_electron(e, dt, volt))
            electrons.add(electron)
            self.add(electron)


        # Wait for 5 seconds with stationary electrons
        self.wait(1)

        # Increase voltage gradually to start motion
        self.play(voltage.animate.set_value(5), run_time=10)
        self.wait(10)




    def create_electron(self):
        """Create an electron at a random position near the cathode."""
        random_offset = np.array([
            np.random.uniform(0, 0.7),  # Left-right variation
            np.random.uniform(-0.5, 0.6),  # Up-down variation
            0
        ])
        start_pos = self.cathode_center + random_offset  # Randomized position
        electron = VGroup(
            Circle(radius=0.1, color=BLUE, fill_opacity=1),
            Text("e⁻", font_size=15).move_to(ORIGIN)
        )
        electron.move_to(start_pos)
        return electron
    

    def update_electron(self, electron, dt, voltage):
        """
        Updater function that continuously moves an electron along a two-phase path:
        - Acceleration phase: from cathode to anode (quadratic interpolation)
        - Constant speed phase: from anode to collector (linear interpolation)
        The electron loops back to the start upon completing a cycle.
        The speed is controlled by the 'voltage' ValueTracker.
        """
        if voltage.get_value() == 0:
            return  # Stay still if voltage is zero
        # Increase the custom timer (scaled by the voltage factor)
        electron.time_elapsed += dt * voltage.get_value()
        # Define a base cycle time (in seconds) for one complete journey
        cycle_time = 3  
        # Use phase_offset to stagger electrons
        effective_time = (electron.time_elapsed + electron.phase_offset) % cycle_time
        progress = effective_time / cycle_time

        # Define the fraction of the cycle for acceleration (cathode -> anode)
        accel_phase = 0.5
        
        if progress < accel_phase:
            # Normalized progress for the acceleration phase (quadratic acceleration)
            norm_prog = progress / accel_phase
            new_pos = electron.start_pos + (self.anode_pos - electron.start_pos) * (norm_prog ** 2)
        else:
            # Normalized progress for the constant-speed phase (linear motion)
            norm_prog = (progress - accel_phase) / (1 - accel_phase)
            new_pos = self.anode_pos + (self.collector_pos - self.anode_pos) * norm_prog
        
        electron.move_to(new_pos)


    def wiggle_electron(self, electron):
        """Wiggle the electron before accelerating."""
        return electron.animate.shift(RIGHT * 0.1).shift(LEFT * 0.1).shift(RIGHT * 0.1)

    def move_electron(self, electron, start, anode, collector):
        """Move electron with acceleration and constant speed."""
        return Succession(
            electron.animate.move_to(anode).set_rate_func(smooth),  # Acceleration to anode
            electron.animate.move_to(collector).set_rate_func(linear),  # Constant speed to collector
            FadeOut(electron)  # Disappear at collector
        )
    
    def create_electronSimple(self, position):
        """Create an electron as a small circle with 'e⁻' inside."""
        return VGroup(
            Circle(radius=0.1, color=BLUE, fill_opacity=1),
            Text("e⁻", font_size=20).move_to(ORIGIN)
        ).move_to(position)
        
    def create_gridded_anode(self):
        """Create a gridded anode as a parallelogram with properly aligned holes."""

        # Define parallelogram points
        p1 = LEFT * 3 + UP * 0.5
        p2 = LEFT * 3 + DOWN * 0.5
        p3 = LEFT * 2.5 + DOWN * 0.2
        p4 = LEFT * 2.5 + UP * 0.8

        # Create parallelogram shape
        anode = Polygon(p1, p2, p3, p4, color=BLUE)
        anode.set_fill(BLUE, opacity=1)

        # Define grid parameters
        rows, cols = 6, 4  # Adjust for hole density
        hole_radius = 0.03

        # Function to transform points to fit parallelogram
        def transform_to_parallelogram(x, y):
            """Transforms a point from a rectangular grid to the parallelogram space."""
            x_ratio = (x + 0.5)  # Normalize x from (-0.5, 0.5) to (0, 1)
            y_ratio = (y + 0.5)  # Normalize y from (-0.5, 0.5) to (0, 1)

            # Linearly interpolate x and y within parallelogram edges
            new_x = (1 - x_ratio) * p1[0] + x_ratio * p3[0]
            new_y = (1 - y_ratio) * p2[1] + y_ratio * p4[1]
            return np.array([new_x, new_y, 0])

        # Generate and transform holes
        holes = VGroup()
        for i in range(rows):
            for j in range(cols):
                x = np.linspace(-0.5, 0.5, rows)[i]  # Normalized x position
                y = np.linspace(-0.5, 0.5, cols)[j]  # Normalized y position
                hole_position = transform_to_parallelogram(x, y)  # Apply transformation
                hole = Circle(radius=hole_radius, color=WHITE, fill_opacity=1).move_to(hole_position)
                holes.add(hole)

        # Group anode with holes
        gridded_anode = VGroup(anode, holes)
        return gridded_anode

    def create_grid_circle(self):
        """Create a simple grid of three circles in one another."""
        grid = VGroup(
            Circle(radius=0.6, color=WHITE, fill_opacity=0.5),
            Circle(radius=0.4, color=WHITE, fill_opacity=0.5),
            Circle(radius=0.2, color=WHITE, fill_opacity=0.5)
        )

        # Apply a perspective transformation matrix
        perspective_matrix = np.array([
            [1, -0.3, 0],
            [0.2, 1, 0],
            [0, 0, 1]
        ])

        grid.apply_matrix(perspective_matrix)
        return grid

    def create_grid(self):
        """Create a grid of horizontal lines, rotated and skewed for perspective."""
        lines = VGroup()
        for y in np.arange(-0.5, 0.6, 0.1):
            line = Line(LEFT * 0.5, RIGHT * 0.5, color=WHITE).shift(UP * y)
            lines.add(line)
    
        # Apply a perspective transformation matrix
        perspective_matrix = np.array([
            [1, 0.1, 0],
            [0.3, 1, 0],
            [0, 0, 1]
        ])
    
        lines.apply_matrix(perspective_matrix)
        return lines




class SingleCollision(Scene):
    def construct(self):
        # Create electron using create_electronSimple function
        electron = self.create_electronSimple(LEFT * 4)

        # Mercury Atom setup
        hg_atom = Circle(radius=1.2, color=GRAY, fill_opacity=1).move_to(RIGHT * 3)
        hg_label = Text("Hg", font_size=50).move_to(hg_atom.get_center())

        # Excited state effect
        excited_glow = Circle(radius=0.7, color=YELLOW, fill_opacity=0.5).move_to(hg_atom)
        excited_glow.set_opacity(0)  # Initially invisible

        # Animation sequence
        self.play(Create(electron))
        self.play(Create(hg_atom), Write(hg_label))

        self.wait(1)

        #write 2ev next to electron
        ev_label = Text("2eV", font_size=30).next_to(electron, LEFT + UP)
        self.play(Write(ev_label))

        self.wait(1)

        # Move electron toward Hg atom
        self.play(electron.animate.move_to(hg_atom.get_center() + LEFT * 1), run_time=1)

        self.wait(0.3)


        #morph 2ev to 4.8eV
        ev_label2 = Text("4.8eV", font_size=30).next_to(electron, LEFT + UP)
        self.play(Transform(ev_label, ev_label2))
        self.wait(0.2)
        # change to 6eV
        ev_label3 = Text("6eV", font_size=30).next_to(electron, LEFT + UP)
        self.play(Transform(ev_label, ev_label3))
        self.wait(0.2)
        # change to 9.6eV
        ev_label4 = Text("9.6eV", font_size=30).next_to(electron, LEFT + UP)
        self.play(Transform(ev_label, ev_label4))
        self.wait(1)



    def create_electronSimple(self, position):
        """Create an electron as a small circle with 'e⁻' inside."""
        return VGroup(
            Circle(radius=0.4, color=BLUE, fill_opacity=1),
            Text("e⁻", font_size=35).move_to(ORIGIN)
        ).move_to(position)


class ChancesAnimation(Scene):
    def construct(self):
        # Define energy level lines and labels (same as before)...
        y_0    = -3          
        y_4_9  = -1          
        y_9_8  = 1           
        y_14_7 = 3           

        line0    = Line(LEFT*8 + UP*y_0, RIGHT*8 + UP*y_0, color=WHITE)
        line4_9  = Line(LEFT*8 + UP*y_4_9, RIGHT*8 + UP*y_4_9, color=YELLOW)
        line9_8  = Line(LEFT*8 + UP*y_9_8, RIGHT*8 + UP*y_9_8, color=YELLOW)
        line14_7 = Line(LEFT*8 + UP*y_14_7, RIGHT*8 + UP*y_14_7, color=YELLOW)
        self.play(Create(line0), Create(line4_9), Create(line9_8), Create(line14_7))

        # Energy level labels
        label0 = Text("0 eV", font_size=24).next_to(line0, DOWN)
        label4_9 = Text("4.9 eV", font_size=24).next_to(line4_9, UP)
        label9_8 = Text("9.8 eV", font_size=24).next_to(line9_8, UP)
        label14_7 = Text("14.7 eV", font_size=24).next_to(line14_7, UP)

        # "n" labels aligned to the left of each line
        label4_9_n = Text("n=1", font_size=24).move_to(LEFT*6 + UP*(y_4_9+0.4))
        label9_8_n = Text("n=2", font_size=24).move_to(LEFT*6 + UP*(y_9_8+0.4))
        label14_7_n = Text("n=3", font_size=24).move_to(LEFT*6 + UP*(y_14_7+0.4))
        self.play(Write(label0), Write(label4_9), Write(label9_8), Write(label14_7))
        self.play(Write(label4_9_n), Write(label9_8_n), Write(label14_7_n))

        start_point = LEFT*7 + UP*y_0
        end_point   = RIGHT*7 + UP*y_0

        # Create a group to store all trails
        all_trails = VGroup()

        # Animate trips without fading any lines; preserve each trail.
        marker_4_9 = self.animate_trip(start_point, end_point, apex_y=y_4_9, run_time=2, color=YELLOW, trail_group=all_trails)
        self.wait(1)

        marker_9_8 = self.animate_trip(start_point, end_point, apex_y=y_9_8, run_time=2, color=YELLOW, trail_group=all_trails)
        self.wait(1)

        marker_14_7 = self.animate_trip(start_point, end_point, apex_y=y_14_7, run_time=2, color=YELLOW, trail_group=all_trails)
        self.wait(2)

        # Finally, add all trails permanently to the scene
        self.add(all_trails)

    def animate_trip(self, start_point, end_point, apex_y, run_time=2, color=YELLOW, trail_group=None):
        """
        Animate a single trip of the electron along a triangular path.
        - Leaves a permanent traced trail.
        - Places a marker at the apex.
        - Adds the trail to trail_group for persistence.
        """
        # Create the electron as a dot
        electron = Dot(point=start_point, color=BLUE)
        
        # Define the key points for the triangular motion
        mid_point = interpolate(start_point, end_point, 0.5)
        apex_point = np.array([mid_point[0], apex_y, 0])

        # Create the triangular path as a VMobject
        triangle_path = VMobject()
        triangle_path.set_points_as_corners([start_point, apex_point, end_point])
        triangle_path.set_color(BLUE)

        # Add electron to the scene
        self.add(electron)

        # Animate the electron along the path while drawing the trail
        self.play(
            MoveAlongPath(electron, triangle_path, run_time=run_time, rate_func=smooth),
            Create(triangle_path, run_time=run_time)  # This animates the path being drawn
        )

        # Add the path to the trail group so it stays
        if trail_group is not None:
            trail_group.add(triangle_path)

        # Place a marker at the apex
        marker = Dot(point=apex_point, color=color)
        self.play(FadeIn(marker))

        return marker


class LambdaFitting(Scene):
    def construct(self):
        # Define initial values
        L_length = 8  # Total distance from cathode to anode
        lambda_length = 1  # Initial lambda length

        # Draw main L line
        L_line = Line(LEFT * L_length / 2, RIGHT * L_length / 2, color=BLUE)

        # Label for L
        L_label = Text("L", font_size=24).next_to(L_line, DOWN)

        # Function to create lambda segments with labels and markers
        def create_lambda_segments(lambda_len):
            segments = VGroup()
            lambda_labels = VGroup()
            markers = VGroup()
            num_lambdas = int(L_length / lambda_len)
            
            for i in range(num_lambdas):
                # Position for lambda segment
                start = LEFT * L_length / 2 + RIGHT * lambda_len * i + UP * 0.4
                end = start + RIGHT * lambda_len
                line = Line(start, end, color=GREEN)
                segments.add(line)

                # Label for lambda segment
                lambda_label = Text("λ", font_size=20).next_to(line, UP, buff=0.1)
                lambda_labels.add(lambda_label)

                # Markers at both ends of the lambda segment
                start_marker = Dot(start, radius=0.05, color=WHITE)
                end_marker = Dot(end, radius=0.05, color=WHITE)
                markers.add(start_marker, end_marker)

            return segments, lambda_labels, markers

        # Initial lambda lines, labels, and markers
        lambda_lines, lambda_labels, lambda_markers = create_lambda_segments(lambda_length)

        # Add elements
        self.add(L_line, L_label, lambda_lines, lambda_labels, lambda_markers)

        # Animate increasing lambda (fewer fit inside L)
        self.wait(1)
        new_lambda_lines, new_lambda_labels, new_lambda_markers = create_lambda_segments(2)  # Larger λ
        self.play(
            Transform(lambda_lines, new_lambda_lines),
            Transform(lambda_labels, new_lambda_labels),
            Transform(lambda_markers, new_lambda_markers),
            run_time=2
        )

        self.wait(2)


class EnergyEquation(Scene):
    def construct(self):
        # Step 1: Initial Equation
        eq1 = MathTex(r"\Delta E = E_n - E_{n-1} = E_a").scale(1.2).move_to(ORIGIN)

        # Step 2: Replace E_a with a ?
        eq2 = MathTex(r"\Delta E = E_n - E_{n-1} = \, ? E_a").scale(1.2).move_to(eq1)

        # Step 3: Replace ? with (2n - 1)
        eq3 = MathTex(r"\Delta E = E_n - E_{n-1} = ?(2n - 1)E_a").scale(1.2).move_to(eq1)

        # Step 4: Add λ/L before (2n - 1)
        eq4 = MathTex(r"\Delta E = E_n - E_{n-1} = \frac{\lambda}{L} (2n - 1)E_a").scale(1.2).move_to(eq1)

        # Step 5: Add +1 before the term
        eq5 = MathTex(r"\Delta E = E_n - E_{n-1} = \left| 1 + \frac{\lambda}{L} (2n - 1) \right| E_a").scale(1.2).move_to(eq1)

        # Step 6: Multiply by E_a
        eq6 = MathTex(r"\Delta E(n) = \left| 1 + \frac{\lambda}{L} (2n - 1) \right| E_a").scale(1.2).move_to(eq1)

        # Step 7: Rearrange to solve for λ
        eq7 = MathTex(r"\lambda = \frac{L}{2E_a} \frac{d\Delta E(n)}{dn}").scale(1.2).move_to(ORIGIN)

        # Animation Sequence
        self.play(Write(eq1))
        self.wait(1)
        self.play(Transform(eq1, eq2))
        self.wait(1)
        self.play(Transform(eq1, eq3))
        self.wait(1)
        self.play(Transform(eq1, eq4))
        self.wait(1)
        self.play(Transform(eq1, eq5))
        self.wait(2)

        # Solve for λ
        self.play(FadeOut(eq1))
        self.play(Write(eq7))
        self.wait(2)


class Introduction(Scene):
    def construct(self):
        # Title
        title = Text("Frank-Hertz Experiment", font_size=40).to_edge(UP)
        self.play(Write(title))

        # Subtitle
        subtitle = Text("An Introduction to Quantum Mechanics", font_size=30).next_to(title, DOWN)
        self.play(Write(subtitle))

        # Introduction text
        intro_text = """
        The Frank-Hertz experiment is a fundamental demonstration of quantum mechanics.
        providing direct evidence of quantized energy levels in atoms.
        """
        intro = Text(intro_text, font_size=24).move_to(ORIGIN)
        self.play(Write(intro), run_time=3)

        self.wait(2)

        # Remove all elements
        self.play(FadeOut(title), FadeOut(subtitle), FadeOut(intro))


