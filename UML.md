# Project UML

```mermaid
classDiagram
    direction TB

    class MainModule {
        +main()
        +_load_coin_progress(raw_data)
        +_serialize_coin_progress(coin_progress)
    }

    class EventLog {
        +max_size: int
        -_log: deque
        +push(message)
        +peek()
        +pop_oldest()
        +clear()
    }

    class SaveManager {
        +filepath: str
        +save(data)
        +load()
        +reset()
        +has_save()
        -_validate(data)
        -_default()
    }

    class MainMenu {
        -_OPTIONS: list
        -_LABELS: list
        +screen
        +save_manager
        +handle_event(event)
        +draw()
    }

    class HUD {
        +screen
        +player
        +level_manager
        +draw()
        -_draw_level_indicator()
        -_draw_coin_counter()
        -_draw_hints()
    }

    class Player {
        +rect: Rect
        +vel_y: float
        +on_ground: bool
        +coins: int
        +update(keys, floor, trampolines)
        +reset(floor)
        +check_on_map(width, height, level_index)
        +draw()
        -_handle_input(keys)
        -_apply_gravity()
        -_move_and_collide(floor)
        -_on_trampoline(trampolines)
    }

    class LevelManager {
        +screen
        +current_index: int
        +collected_coins: dict
        -_registry: OrderedDict
        -_current_level: Level
        +get_current_floor()
        +get_current_coins()
        +get_current_trampolines()
        +collect_current_coins(player_rect)
        +draw()
        +next_level()
        +previous_level()
        +get_current_level()
        +total_levels()
        -_load_level(level_index)
    }

    class Level {
        <<abstract>>
        +screen
        +floor: list
        +coins: list
        +trampolines: list
        +TILE: int
        +H: int
        +W: int
        +build_floor()
        +draw()
        +get_floor()
        +get_coins()
        +get_trampolines()
        +apply_collected_coin_ids(collected_ids)
        +collect_coins(player_rect)
        -_add_ground_run(start_x, end_x)
        -_add_platform(x, y, tiles_wide)
        -_add_trampoline(x, y, width)
        -_add_coin(x, y, coin_id)
    }

    class FirstLevel
    class SecondLevel
    class ThirdLevel
    class FourthLevel
    class FifthLevel

    class Coin {
        +coin_id: str
        +collected: bool
        +rect: Rect
        +try_collect(player_rect)
        +draw(screen)
    }

    class Trampoline {
        +BOUNCE_VELOCITY: int
        +STRETCH_FRAMES: int
        +rect: Rect
        +apply_bounce(player)
        +update()
        +draw(screen)
    }

    MainModule ..> LevelManager : creates
    MainModule ..> Player : creates
    MainModule ..> SaveManager : uses
    MainModule ..> MainMenu : uses
    MainModule ..> HUD : uses
    MainModule ..> EventLog : uses

    MainMenu --> SaveManager : checks save
    HUD --> Player : reads stats
    HUD --> LevelManager : reads level state

    LevelManager *-- Level : owns current level
    LevelManager ..> FirstLevel : registry
    LevelManager ..> SecondLevel : registry
    LevelManager ..> ThirdLevel : registry
    LevelManager ..> FourthLevel : registry
    LevelManager ..> FifthLevel : registry

    Level <|-- FirstLevel
    Level <|-- SecondLevel
    Level <|-- ThirdLevel
    Level <|-- FourthLevel
    Level <|-- FifthLevel

    Level *-- Coin : contains
    Level *-- Trampoline : contains

    Player ..> Trampoline : bounces on
    Player ..> Level : collides with floor data
```

## Notes

- `Main.py` is the entry point and orchestrates menu, gameplay, saving, and win/lose states.
- `LevelManager` owns the currently active `Level` and re-applies collected coin state when levels change.
- `Level` is the abstract base for all five stage classes and contains the shared helpers for floor, coins, and trampolines.
- `Player`, `Coin`, and `Trampoline` drive the main in-level gameplay interactions.
