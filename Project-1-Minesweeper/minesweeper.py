import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        # If the number of cells equals the count, all cells are mines
        if self.count == len(self.cells) and len(self.cells) > 0:
            return self.cells.copy()
        return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        # If the count is 0, all cells are safe
        if self.count == 0:
            return self.cells.copy()
        return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def get_neighbors(self, cell):
        """
        Returns all neighbors of a given cell.
        """
        i, j = cell
        neighbors = set()

        for di in range(-1, 2):
            for dj in range(-1, 2):
                if di == 0 and dj == 0:
                    continue
                ni, nj = i + di, j + dj
                if 0 <= ni < self.height and 0 <= nj < self.width:
                    neighbors.add((ni, nj))

        return neighbors

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        # 1. Mark cell as made move
        self.moves_made.add(cell)

        # 2. Mark cell as safe
        self.mark_safe(cell)

        # 3. Add new sentence based on cell and count
        neighbors = self.get_neighbors(cell)
        
        # Only include cells whose state is still undetermined
        undetermined_neighbors = set()
        for neighbor in neighbors:
            if neighbor not in self.mines and neighbor not in self.safes:
                undetermined_neighbors.add(neighbor)

        # Count mines among neighbors
        mine_count = 0
        for neighbor in neighbors:
            if neighbor in self.mines:
                mine_count += 1

        # Create new sentence with remaining undetermined cells
        new_sentence = Sentence(undetermined_neighbors, count - mine_count)
        if len(new_sentence.cells) > 0:
            self.knowledge.append(new_sentence)

        # 4 & 5. Iterate until no new inferences can be made
        changed = True
        while changed:
            changed = False

            # Check for new mines and safes from all sentences
            new_mines = set()
            new_safes = set()

            for sentence in self.knowledge:
                # Find known mines
                mines = sentence.known_mines()
                if mines:
                    new_mines.update(mines)

                # Find known safes
                safes = sentence.known_safes()
                if safes:
                    new_safes.update(safes)

            # Mark any new mines
            for mine in new_mines:
                if mine not in self.mines:
                    self.mark_mine(mine)
                    changed = True

            # Mark any new safes
            for safe in new_safes:
                if safe not in self.safes:
                    self.mark_safe(safe)
                    changed = True

            # Remove empty sentences
            self.knowledge = [s for s in self.knowledge if len(s.cells) > 0]

            # Infer new sentences using subset method
            new_knowledge = []

            # Compare all pairs of sentences
            for i in range(len(self.knowledge)):
                for j in range(i + 1, len(self.knowledge)):
                    set1 = self.knowledge[i].cells
                    set2 = self.knowledge[j].cells
                    count1 = self.knowledge[i].count
                    count2 = self.knowledge[j].count

                    # If set1 is subset of set2
                    if set1.issubset(set2):
                        new_cells = set2 - set1
                        new_count = count2 - count1
                        if new_cells:
                            new_sentence = Sentence(new_cells, new_count)
                            if new_sentence not in self.knowledge and new_sentence not in new_knowledge:
                                new_knowledge.append(new_sentence)
                                changed = True

                    # If set2 is subset of set1
                    elif set2.issubset(set1):
                        new_cells = set1 - set2
                        new_count = count1 - count2
                        if new_cells:
                            new_sentence = Sentence(new_cells, new_count)
                            if new_sentence not in self.knowledge and new_sentence not in new_knowledge:
                                new_knowledge.append(new_sentence)
                                changed = True

            # Add new inferred sentences
            if new_knowledge:
                self.knowledge.extend(new_knowledge)

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        for safe in self.safes:
            if safe not in self.moves_made:
                return safe
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        all_cells = set()
        for i in range(self.height):
            for j in range(self.width):
                all_cells.add((i, j))

        # Remove cells that are already made or known mines
        available = all_cells - self.moves_made - self.mines

        if not available:
            return None

        return random.choice(list(available))