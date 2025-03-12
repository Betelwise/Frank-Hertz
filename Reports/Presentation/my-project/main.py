from manim import *
import numpy as np

class FrankHertzMain(Scene):
    def construct(self):
        # Step 1: Create the Housing (Vacuum Tube)
        housing = RoundedRectangle(height=3, width=8, corner_radius=0.3, color=WHITE)
        
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
        anode = self.create_gridded_anode().move_to(ORIGIN)
        collector = cathode.copy().set_color(GREEN).move_to(RIGHT * 3)
        
        # Step 3: Create the Knob (Voltage Control)
        knob = Circle(radius=0.3, color=YELLOW).move_to(UP * 2)
        knob_label = Text("Voltage", font_size=24).next_to(knob, UP)
        

        # Animation Sequence 1: Housing, Cathode, and Filament Appear
        self.play(Create(cathode), Create(filament), Create(housing))
        # self.play(FadeIn(cathode), FadeIn(filament))
        # self.wait(1)


        # Animation Sequence 2: Filament Heats Up
        glowing_filament = filament.copy().set_color(YELLOW)
        self.play(Transform(filament, glowing_filament), run_time=1)
        self.wait(1)

        #create the anode and collector
        self.play(Create(anode), Create(collector))
        self.wait(1)

        # Create a ValueTracker to control the speed (voltage)
        voltage = ValueTracker(1)  # Change this value to speed up or slow down electrons
        # Define key positions along the electron path:
        # self.cathode_pos = LEFT * 3.2
        self.cathode_center = LEFT * 3.2
        self.anode_pos = ORIGIN
        self.collector_pos = RIGHT * 3
        # Step 6: Create Electrons One After Another
        electrons = VGroup()
        num_electrons = 10
        # for i in range(num_electrons):
        #     # rnd = np.random.uniform(-0.5, 0.5)
        #     # rnd2 = np.random.uniform(-0.5, 0.5)
        #     # Random offsets for spawning position
        #     random_offset = np.array([
        #         np.random.uniform(-0.3, 0.3),  # Left-right variation
        #         np.random.uniform(-1, 1),  # Up-down variation
        #         0  # Z-axis remains 0
        #     ])
        #     start_pos = self.cathode_center + random_offset  # Apply random offset
        #     # electron = self.create_electron(LEFT * (2.5 + rnd*0.5) + UP * (1 * 0.2)+rnd2)
        #     electron = self.create_electron(start_pos)
        #     # Initialize a custom time counter for each electron
        #     electron.time_elapsed = 0
        #     # Optionally add a random phase offset (to stagger the electrons)
        #     electron.phase_offset = np.random.uniform(0, 3)
        #     # Attach an updater that moves the electron along the path
        #     electron.add_updater(lambda e, dt, volt=voltage: self.update_electron(e, dt, volt))
        #     electrons.add(electron)
        #     self.add(electron)
        for i in range(num_electrons):
            electron = self.create_electron()
            electron.time_elapsed = 0
            electron.phase_offset = np.random.uniform(0, 3)  # Staggered start times
            electron.add_updater(lambda e, dt, volt=voltage: self.update_electron(e, dt, volt))
            electrons.add(electron)
            self.add(electron)
            # self.play(Create(electron), run_time=0.1)
        # # Animation Sequence 5: Increase Voltage and Accelerate Electrons
        # electron_animations = [
        #     self.move_electron(electron, LEFT * 3.2, ORIGIN, RIGHT * 3).set_run_time(3)
        #     for electron in electrons
        # ]
        # Use a lag_ratio less than 1 (e.g., 0.3) for overlapping animations.
        # self.play(AnimationGroup(*electron_animations, lag_ratio=0.05))
        self.wait(5)
        voltage.set_value(2)
        self.wait(5)
        voltage.set_value(3)
        self.wait(5)

from manim import *

class Collision(Scene):
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




        # # Animation Sequence 5: Increase Voltage and Accelerate Electrons
        # for electron in electrons:
        #     self.play(self.move_electron(electron, LEFT * 3.2, ORIGIN, RIGHT * 3), run_time=3, rate_func=smooth)
        
        # self.wait(2)
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


    def create_electronSimple(self, position):
        """Create an electron as a small circle with 'e⁻' inside."""
        return VGroup(
            Circle(radius=0.4, color=BLUE, fill_opacity=1),
            Text("e⁻", font_size=35).move_to(ORIGIN)
        ).move_to(position)
    
    def create_electron(self):
        """Create an electron at a random position near the cathode."""
        random_offset = np.array([
            np.random.uniform(-0.3, 0.3),  # Left-right variation
            np.random.uniform(-1, 1),  # Up-down variation
            0
        ])
        start_pos = self.cathode_center + UP * 2
        electron = VGroup(
            Circle(radius=0.1, color=BLUE, fill_opacity=1),
            Text("e⁻", font_size=15).move_to(ORIGIN)
        )
        electron.move_to(start_pos)
        return electron

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
        
    def update_electron(self, electron, dt, voltage):
        """
        Updater function that continuously moves an electron along a two-phase path:
        - Acceleration phase: from cathode to anode (quadratic interpolation)
        - Constant speed phase: from anode to collector (linear interpolation)
        The electron loops back to the start upon completing a cycle.
        The speed is controlled by the 'voltage' ValueTracker.
        """
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
            new_pos = self.cathode_center + (self.anode_pos - self.cathode_center) * (norm_prog ** 2)
        else:
            # Normalized progress for the constant-speed phase (linear motion)
            norm_prog = (progress - accel_phase) / (1 - accel_phase)
            new_pos = self.anode_pos + (self.collector_pos - self.anode_pos) * norm_prog
        
        electron.move_to(new_pos)