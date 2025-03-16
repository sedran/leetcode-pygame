import pygame

from leetcode_pygame.bfs_shortest_path.constants import (
    FPS,
    SCREEN_SIZE,
)


class Game:
    def __init__(self):
        # Currently active state
        self.state = None

        # Next state to activate at the end of the game loop iteration
        self.next_state = None

        # Is the game running?
        self.running = False

        # Game's main screen; main surface to draw our game into
        self.screen = None

    def run(self):
        # Before doing anything else with pygame, it must be initialized
        pygame.init()

        # Define the screen and its size
        self.screen = pygame.display.set_mode(SCREEN_SIZE)

        # This sets the text on the title bar of the window
        pygame.display.set_caption("Shortest Path in Binary Matrix")

        # Update the contents of the entire display
        pygame.display.flip()

        # Clock will help us keep track of time and handle frame rate
        clock = pygame.time.Clock()

        # Set running to True to go into the infinite gaming loop until running is False
        self.running = True

        # Initialise the InitState: entrance scene for the game
        from leetcode_pygame.bfs_shortest_path.states import InitState

        self.state = InitState(self)

        # Start the gaming loop; run the code until running=False
        while self.running:
            # We do two things here: first, ask clock to update and regulate the frame rate,
            # then we calculate the deltaTime (elapsed time) in seconds.
            #
            # clock.tick(FPS) ensures that the game runs at the specified FPS (frames per second),
            # by limiting the number of frames that can be drawn within a given time.
            #
            # The resulting delta_time is the time in seconds between the current frame and the previous frame.
            # This value can be used for frame rate-independent movement or other time-dependent operations.
            # Dividing by 1000 converts the result from milliseconds to seconds,
            # which is a standard unit of time for physics simulations.
            #
            # The value of delta_time can be used for smooth animations, physics calculations, or any other task
            # that requires time-based adjustments that are not dependent on the actual frame rate.
            delta_time = clock.tick(FPS) / 1000  # deltaTime in seconds
            print("FPS: ", clock.get_fps(), "Delta time: ", delta_time)

            # Game loops typically have 3 main actions: handling events, updating game state, and rendering.
            # Handle input events (e.g., keyboard, mouse) and game logic changes.
            self.handle_events()

            # Update the current game state based on the elapsed time (delta_time),
            # ensuring frame rate independence for physics, movements, or logic.
            self.state.update(delta_time)

            # Render the updated state to the screen (draw the updated visuals or objects).
            self.state.render()

            # Flip the display buffers to update the screen with the new frame.
            # This is typically used in double-buffered rendering to prevent flickering.
            pygame.display.flip()

            # Check if there is a state change request pending.
            if self.next_state is not None:
                # Transition to the new state by updating the current state.
                self.state = self.next_state

                # Reset the next_state to None, clearing the transition request.
                self.next_state = None

        # Quit the game, terminates the window. We need to call this when the game loop ends.
        # Otherwise, the window stays open.
        pygame.quit()

    def handle_events(self):
        # Initialize an empty list to store the events to be processed.
        events = []

        # Loop through all events in the event queue.
        for event in pygame.event.get():
            # If the event is a quit event (e.g., closing the window).
            if event.type == pygame.QUIT:
                # Set the running flag to False to stop the game loop.
                self.running = False
                # Exit the method immediately to stop handling further events.
                return
            else:
                # Add all other events to the events list for further processing.
                events.append(event)

        # Pass the collected events to the current game state's handle_events method for processing.
        self.state.handle_events(events)


if __name__ == "__main__":
    # Create an instance of the Game class, initializing the game object.
    game = Game()

    # Call the run method to start the game loop and begin game execution.
    game.run()
