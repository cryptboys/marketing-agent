import os
import importlib.util

class SkillManager:
    def __init__(self, skills_dir='skills'):
        self.skills_dir = skills_dir
        self.loaded_skills_instances = {}
        self.loaded_skills_modules = {}  # keep module refs too
        self.load_skills()

    def load_skills(self):
        if not os.path.exists(self.skills_dir):
            print(f"Skills directory '{self.skills_dir}' not found.")
            return
        for skill_file in os.listdir(self.skills_dir):
            if skill_file.endswith('.py') and not skill_file.startswith('__'):
                module_name = skill_file[:-3]
                try:
                    spec = importlib.util.spec_from_file_location(
                        f"skills.{module_name}",
                        os.path.join(self.skills_dir, skill_file)
                    )
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    self.loaded_skills_modules[module_name] = module
                    # store module itself under both names so any top-level attr works
                    self.loaded_skills_instances[module_name] = module
                    self.loaded_skills_instances[module_name.replace('_', '-')] = module
                    print(f"Loaded skill: {module_name}")
                except Exception as e:
                    print(f"Error loading skill {skill_file}: {e}")

    def get_skill_instance(self, skill_name):
        return self.loaded_skills_instances.get(skill_name)

    def get_skill_module(self, skill_name):
        return self.loaded_skills_modules.get(skill_name)


skill_manager = SkillManager()
