from mesa import Agent

class SimplePrey(Agent):
    def __init__(self, model):
        super().__init__(model)

    def move(self):
        possible_steps = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False
        )
        if possible_steps:
            new_position = self.random.choice(possible_steps)
            self.model.grid.move_agent(self, new_position)

    def step(self):
        if self.pos is None: return
        self.move()
        
        if self.random.random() < self.model.alpha:
            baby = self.__class__(self.model)
            self.model.grid.place_agent(baby, self.pos)

class SimplePredator(Agent):
    def __init__(self, model):
        super().__init__(model)

    def move(self):
        possible_steps = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False
        )
        if possible_steps:
            new_position = self.random.choice(possible_steps)
            self.model.grid.move_agent(self, new_position)

    def step(self):
        if self.pos is None: return
        self.move()
        
        cellmates = self.model.grid.get_cell_list_contents([self.pos])
        prey_list = [obj for obj in cellmates if isinstance(obj, SimplePrey)]
        
        if prey_list:
            victim = self.random.choice(prey_list)
            self.model.grid.remove_agent(victim)
            victim.remove() 
            
            if self.random.random() < self.model.delta:
                baby = self.__class__(self.model)
                self.model.grid.place_agent(baby, self.pos)
                
        elif self.random.random() < getattr(self.model, 'gamma', 0.1):
            self.model.grid.remove_agent(self)
            self.remove()

class ParadoxPrey(SimplePrey):
    def step(self):
        if self.pos is None: return
        self.move()
        
        total_prey = getattr(self.model, "current_prey_count", 0)
        k_global_limit = getattr(self.model, "carrying_capacity", 1000)
        
        if total_prey < k_global_limit:
            alpha = getattr(self.model, "alpha", 0.1)
            if self.random.random() < alpha:
                baby = self.__class__(self.model)
                self.model.grid.place_agent(baby, self.pos)

class ParadoxPredator(Agent):
    def __init__(self, model):
        super().__init__(model)
        self.energy = 20
        self.handling_time_remaining = 0

    def move(self):
        possible_steps = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False
        )
        if possible_steps:
            new_position = self.random.choice(possible_steps)
            self.model.grid.move_agent(self, new_position)

    def step(self):
        if self.pos is None: return
        self.move()
        
        self.energy -= 1  
        
        # Holling Type II: Si el depredador está "manipulando/digiriendo", no caza
        if self.handling_time_remaining > 0:
            self.handling_time_remaining -= 1
        else:
            # Si no está digiriendo, busca presas en su celda
            cellmates = self.model.grid.get_cell_list_contents([self.pos])
            prey_list = [obj for obj in cellmates if isinstance(obj, ParadoxPrey)]

            if prey_list:
                victim = self.random.choice(prey_list)
                self.model.grid.remove_agent(victim)
                victim.remove()
                
                delta = getattr(self.model, "delta", 5)
                self.energy += delta
                
                # Inicia el tiempo de manipulación (handling time) 
                handling_time = getattr(self.model, "handling_time", 1)
                self.handling_time_remaining = handling_time

        if self.energy > 30:
            self.energy -= 15
            baby = self.__class__(self.model)
            self.model.grid.place_agent(baby, self.pos)

        if self.energy <= 0:
            self.model.grid.remove_agent(self)
            self.remove()            

class Prey(Agent):
    def __init__(self, model):
        super().__init__(model)
        self.energy = 10 

    def move(self):
        possible_steps = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False
        )
        new_position = self.random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)

    def step(self):
        if self.pos is None: return
        self.move()
        
        modo_global = getattr(self.model, "use_global_k", False)
        can_reproduce = False
        
        if modo_global:
            total_prey = self.model.current_prey_count
            k_global_limit = getattr(self.model, "carrying_capacity", 1000)
            if total_prey < k_global_limit:
                can_reproduce = True
        else:
            cellmates = self.model.grid.get_cell_list_contents([self.pos])
            local_prey_count = sum(1 for obj in cellmates if isinstance(obj, Prey))
            k_local = getattr(self.model, "k_local", 2)
            if local_prey_count < k_local:
                can_reproduce = True
        
        if can_reproduce:
            alpha = getattr(self.model, "alpha_prey_growth", 0.05)
            if self.random.random() < alpha:
                neighborhood = list(self.model.grid.get_neighborhood(
                    self.pos, moore=True, include_center=True
                ))
                neighbors_content = self.model.grid.get_cell_list_contents(neighborhood)
                partners = [
                    obj for obj in neighbors_content
                    if isinstance(obj, self.__class__) and obj is not self
                ]
                if partners:
                    partner = self.random.choice(partners)
                    self.energy -= 1
                    partner.energy -= 1
                    if self.energy > 0 and partner.energy > 0:
                        baby = self.__class__(self.model)
                        self.model.grid.place_agent(baby, self.pos)

class Predator(Agent):
    def __init__(self, model):
        super().__init__(model)
        self.energy = 20

    def move(self):
        possible_steps = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False
        )
        new_position = self.random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)

    def step(self):
        if self.pos is None: return
        self.move()
        self.energy -= 1  

        cellmates = self.model.grid.get_cell_list_contents([self.pos])
        prey_list = [obj for obj in cellmates if isinstance(obj, Prey)]

        if len(prey_list) > 0:
            victim = self.random.choice(prey_list)
            
            self.model.grid.remove_agent(victim)
            victim.remove() 
            
            self.energy += self.model.delta_predator_gain

        if self.energy > 30: 
            neighborhood = list(self.model.grid.get_neighborhood(
                self.pos, moore=True, include_center=True
            ))
            neighbors_content = self.model.grid.get_cell_list_contents(neighborhood)
            partners = [
                obj for obj in neighbors_content
                if isinstance(obj, self.__class__) and obj is not self
            ]
            if partners:
                partner = self.random.choice(partners)
                self.energy -= 15
                partner.energy -= 15
                if self.energy > 0 and partner.energy > 0:
                    baby = self.__class__(self.model)
                    self.model.grid.place_agent(baby, self.pos)

        if self.energy <= 0:
            self.model.grid.remove_agent(self)
            self.remove() 

class RefugePredator(Predator):
    def move(self):
        possible_steps = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False
        )
        
        valid_steps = [pos for pos in possible_steps if pos not in self.model.refuge_cells]
        
        if len(valid_steps) > 0:
            new_position = self.random.choice(valid_steps)
            self.model.grid.move_agent(self, new_position)

class MountainPrey(Prey):
    def move(self):
        possible_steps = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False
        )
        safe_steps = [p for p in possible_steps if p in self.model.refuge_cells]
        
        if safe_steps and self.random.random() < 0.95:
            new_pos = self.random.choice(safe_steps)
        else:
            new_pos = self.random.choice(possible_steps)
            
        self.model.grid.move_agent(self, new_pos)

    def step(self):
        if self.pos is None: return
        self.move()
        
        if self.pos not in self.model.refuge_cells:
            if self.random.random() < 0.3: 
                self.model.grid.remove_agent(self)
                self.remove()
                return 

        if self.random.random() < 0.08: 
            neighborhood = list(self.model.grid.get_neighborhood(
                self.pos, moore=True, include_center=True
            ))
            neighbors_content = self.model.grid.get_cell_list_contents(neighborhood)
            partners = [
                obj for obj in neighbors_content
                if isinstance(obj, self.__class__) and obj is not self
            ]
            if partners:
                partner = self.random.choice(partners)
                self.energy -= 1
                partner.energy -= 1
                if self.energy > 0 and partner.energy > 0:
                    baby = self.__class__(self.model)
                    self.model.grid.place_agent(baby, self.pos)
        
        cellmates = self.model.grid.get_cell_list_contents([self.pos])
        prey_on_cell = [obj for obj in cellmates if isinstance(obj, Prey)]
        if len(prey_on_cell) > 3: 
             if self.random.random() < 0.5: 
                self.model.grid.remove_agent(self)
                self.remove()

class TerritorialPredator(Predator):
    def __init__(self, model):
        super().__init__(model)
        self.energy = 60

    def move(self):
        possible_steps = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False
        )
        valid_steps = []
        for p in possible_steps:
            is_in_refuge = p in self.model.refuge_cells
            is_in_island = p in self.model.island_cells
            if is_in_refuge and not is_in_island: continue
            valid_steps.append(p)
            
        if not valid_steps: return

        hunting_grounds = [p for p in valid_steps if p in self.model.island_cells]
        if hunting_grounds and self.random.random() < 0.8:
            new_pos = self.random.choice(hunting_grounds)
        else:
            new_pos = self.random.choice(valid_steps)
        self.model.grid.move_agent(self, new_pos)

    def step(self):
        if self.pos is None: return 
        self.move()
        
        self.energy -= 2 
        
        cellmates = self.model.grid.get_cell_list_contents([self.pos])
        prey = [obj for obj in cellmates if isinstance(obj, Prey)]
        if prey:
            victim = self.random.choice(prey)
            self.model.grid.remove_agent(victim)
            victim.remove()
            self.energy += 40
            
        if self.energy <= 0:
            self.model.grid.remove_agent(self)
            self.remove()
            return
        
        if self.energy > 250:
            neighborhood = list(self.model.grid.get_neighborhood(
                self.pos, moore=True, include_center=True
            ))
            neighbors_content = self.model.grid.get_cell_list_contents(neighborhood)
            partners = [
                obj for obj in neighbors_content
                if isinstance(obj, self.__class__) and obj is not self
            ]
            if partners:
                partner = self.random.choice(partners)
                self.energy -= 100
                partner.energy -= 100
                if self.energy > 0 and partner.energy > 0:
                    baby = self.__class__(self.model)
                    self.model.grid.place_agent(baby, self.pos)

