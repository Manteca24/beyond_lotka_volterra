from mesa import Model
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from agent import Prey, Predator, RefugePredator, MountainPrey, TerritorialPredator, SimplePrey, SimplePredator, ParadoxPrey, ParadoxPredator

class LotkaVolterraModel(Model):
    def __init__(self, N_prey, N_predator, width, height, alpha, delta, gamma, seed=None):
        super().__init__(seed=seed)
        self.num_prey = N_prey
        self.num_predator = N_predator
        self.grid = MultiGrid(width, height, torus=True)
        self.running = True

        self.alpha = alpha
        self.delta = delta
        self.gamma = gamma

        for i in range(self.num_prey):
            a = SimplePrey(self) 
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))

        for i in range(self.num_predator):
            a = SimplePredator(self)
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))

        self.datacollector = DataCollector(
            model_reporters={
                "Prey": lambda m: len([a for a in m.agents if isinstance(a, SimplePrey)]),
                "Predator": lambda m: len([a for a in m.agents if isinstance(a, SimplePredator)])
            }
        )

    def step(self):
        self.datacollector.collect(self)
        
        self.agents.shuffle_do("step")
        
        if len(self.agents) == 0:
            self.running = False

    @staticmethod
    def count_type(model, agent_type):
        return sum([1 for a in model.agents if isinstance(a, agent_type)])       


class LogisticHollingModel(Model):
    def __init__(self, N_prey, N_predator, width, height, alpha=0.1, delta=5, k_local=4, use_global_k=False, k_global_factor=0.5, seed=None):
        super().__init__(seed=seed)
        
        self.use_global_k = use_global_k
        self.k_local = k_local
        self.alpha_prey_growth = alpha
        self.delta_predator_gain = delta
        
        if self.use_global_k:
            self.prey_class = ParadoxPrey
            self.pred_class = ParadoxPredator
            self.carrying_capacity = k_global_factor * (width * height)
        else:
            self.prey_class = Prey
            self.pred_class = Predator
            
        self.grid = MultiGrid(width, height, torus=True)
        self.running = True
        self.current_prey_count = N_prey
        self.num_predator = N_predator
        
        for i in range(N_prey):
            a = self.prey_class(self) 
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))

        for i in range(N_predator):
            a = self.pred_class(self)
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(a, (x, y))
        self.datacollector = DataCollector(
            {
             "Prey": lambda m: self.count_type(m, self.prey_class),
             "Predator": lambda m: self.count_type(m, self.pred_class)
            }
        )

    def step(self):
        self.current_prey_count = self.count_type(self, self.prey_class)
        self.agents.shuffle_do("step")        
        if self.count_type(self, self.prey_class) == 0 or self.count_type(self, self.pred_class) == 0:
            self.running = False

        self.datacollector.collect(self)

    @staticmethod
    def count_type(model, agent_type):
        return sum([1 for a in model.agents if isinstance(a, agent_type)])

class RefugeModel(LogisticHollingModel):
    def __init__(self, N_prey, N_predator, width, height, alpha=0.1, delta=5, refuge_density=0.2):
        super().__init__(N_prey, N_predator, width, height, alpha, delta)
        
        self.refuge_cells = []
        for x in range(width):
            for y in range(height):
                if self.random.random() < refuge_density:
                    self.refuge_cells.append((x, y))
        
        for agent in list(self.agents):
            if isinstance(agent, Predator) and not isinstance(agent, Prey): 
                agent.remove() 
                
        for i in range(self.num_predator):
            predator = RefugePredator(self)
            
            placed = False
            while not placed:
                x = self.random.randrange(self.grid.width)
                y = self.random.randrange(self.grid.height)
                
                if (x, y) not in self.refuge_cells:
                    self.grid.place_agent(predator, (x, y))
                    placed = True

class SanctuaryModel(LogisticHollingModel):

    def __init__(self, N_prey, N_predator, width, height, alpha=0.1, delta=5, refuge_width_pct=0.3):
        super().__init__(N_prey, N_predator, width, height, alpha, delta)
        
        self.refuge_cells = []
        
        sanctuary_cols = int(width * refuge_width_pct)
        
        for x in range(sanctuary_cols):
            for y in range(height):
                self.refuge_cells.append((x, y))
        
        for agent in list(self.agents):
            if isinstance(agent, Predator) and not isinstance(agent, Prey):
                agent.remove()
        
        for i in range(self.num_predator):
            predator = RefugePredator(self)
            
            placed = False
            while not placed:
                if sanctuary_cols < width:
                    x = self.random.randrange(sanctuary_cols, width) 
                else:
                    x = width - 1 
                    
                y = self.random.randrange(self.grid.height)
                
                self.grid.place_agent(predator, (x, y))
                placed = True

class FilterCorridorModel(LogisticHollingModel):
    def __init__(self, N_prey, N_predator, width=30, height=30, corridor_active=False):
        super().__init__(0, 0, width, height)
        
        self.island_cells = []   
        self.refuge_cells = []   
        
        patch_1 = [(x, y) for x in range(3, 8) for y in range(22, 27)] 
        patch_2 = [(x, y) for x in range(22, 27) for y in range(3, 8)]
        
        self.island_cells.extend(patch_1)
        self.island_cells.extend(patch_2)
        self.refuge_cells.extend(self.island_cells)
        
        if corridor_active:
            for i in range(5, 25):
                center_y = 29 - i
                if 0 <= i < width and 0 <= center_y < height:
                    pts = [(i, center_y), (i+1, center_y)]
                    for p in pts:
                        if p not in self.refuge_cells:
                            self.refuge_cells.append(p)
        
        for _ in range(50): 
            a = MountainPrey(self) 
            start_pos = self.random.choice(self.island_cells)
            self.grid.place_agent(a, start_pos)
            
        for _ in range(8): 
            a = TerritorialPredator(self)
            start_pos = self.random.choice(self.island_cells)
            self.grid.place_agent(a, start_pos)
