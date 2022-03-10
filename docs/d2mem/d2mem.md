Module d2mem.d2mem
==================
read_mem.py - Simple docs generator for Python code documented to Google docstring standard.

Classes
-------

`d2r_proc()`
:   Some doc string
    Args:
        c (str): some a.
        b (str): some b.
        a (str): some c.
    Returns:
        something I hope

    ### Methods

    `chest_dist(self)`
    :   doc string

    `find_info(self)`
    :   Summary
        
        Returns:
            TYPE: Description

    `find_items(self)`
    :   Summary

    `find_mobs(self)`
    :   Summary

    `find_objects(self, file_number: int)`
    :   Summary
        
        Args:
            file_number (int): Description
        
        Returns:
            TYPE: Description

    `get_current_level(self)`
    :   Summary

    `get_exp_offset(self)`
    :   Summary
        
        Returns:
            TYPE: Description

    `get_game_info_offset(self)`
    :   Summary
        
        Returns:
            TYPE: Description

    `get_hover_object_offset(self)`
    :   Summary
        
        Returns:
            TYPE: Description

    `get_last_hovered(self)`
    :   Summary

    `get_map_d2api(self, seed)`
    :   Get map values for input seed, using the piped api
        
        Args:
            seed (uint): current map seed

    `get_map_json(self, seed, mapid: int, objectIDs: list = None)`
    :   Summary
        
        Args:
            seed (TYPE): current map seed read from memory
            mapid (int): current in game map number
            objectIDs (list, optional): Description
        
        Returns:
            TYPE: Description

    `get_map_json_exit(self, seed, mapid: int, objectIDs: list = None)`
    :   Summary
        
        Args:
            seed (TYPE): Description
            mapid (int): Description
            objectIDs (list, optional): Description
        
        Returns:
            TYPE: Description

    `get_menu_data_offset(self)`
    :   Summary
        
        Returns:
            TYPE: Description

    `get_menu_vis_offset(self)`
    :   Summary
        
        Returns:
            TYPE: Description

    `get_player_offset(self, loops)`
    :   Summary
        
        Args:
            loops (TYPE): Description
        
        Returns:
            TYPE: Description

    `get_ppos(self)`
    :   Summary

    `get_ui_settings_offset(self)`
    :   Summary
        
        Returns:
            TYPE: Description

    `get_unit_offset(self)`
    :   doc string
        
        Returns:
            TYPE: Description

    `normalized_p(self)`
    :   Summary

    `read_loot_cfg(self)`
    :

    `ui_status(self)`
    :   Summary