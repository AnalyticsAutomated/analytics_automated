import inspect
from django.apps import AppConfig

import analytics_automated.validators


class startup(AppConfig):
    name = "analytics_automated"
    verbose_name = "Initialise Validator Table"
    ready_run = False

    def ready(self):
        if self.ready_run:
            return
        self.ready_run = True

        try:
            functionList = inspect.getmembers(analytics_automated.validators,
                                              inspect.isfunction)
            validatorList = [seq[0] for seq in functionList]
            validator_types = AppConfig.get_model(self, "ValidatorTypes")
            existing_entries = validator_types.objects.all().values_list('name')


            existing_types = [seq[0] for seq in existing_entries]
            for this_type in existing_types:
                print("Existing validator: "+str(this_type))
                if this_type in validatorList:
                    continue
                else:
                    print("Removing removed validator: "+this_type)
                    validator_types.objects.filter(name=this_type).delete()

            for validator in validatorList:
                if validator in existing_types:
                    continue
                else:
                    print("Registering New Validator Type: "+validator)
                    validator_types.objects.create(name=validator)
        except:
            print("First time eh?")
