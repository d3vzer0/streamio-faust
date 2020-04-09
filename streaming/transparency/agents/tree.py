from streaming.app import app, logger
from streaming.config import config
from streaming.transparency.api.request import async_request
from streaming.transparency.topics import (
    Operators, States, states_table,
    operators_topic, states_topic, tree_topic,
    Tree
)
import faust

# Get tree size for each operator log
@app.agent(operators_topic, concurrency=20)
async def get_tree_size(operators: faust.Stream[Operators]):
    async for operator in operators:
        # Get the latest record count for the log
        get_state = await async_request(f'{operator.log}ct/v1/get-sth')
        if get_state: await tree_topic.send(value={'log': operator.log, **get_state})

@app.agent(tree_topic)
async def compare_tree(treesizes: faust.Stream[Tree]):
    max_drift = config['transparency']['max_drift']
    async for tree in treesizes.group_by(Tree.log):
        if tree.log not in states_table:
            logger.info(f'log={tree.log}, tree_size={tree.tree_size}, action=update, type=tree')
            states_table[tree.log] = tree.tree_size

        elif tree.tree_size > states_table[tree.log]:
            if tree.tree_size > (states_table[tree.log] + max_drift):
                logger.warn(f'log={tree.log}, new_size={tree.tree_size}, old_size={states_table[tree.log]}, action=drift, type=tree')
                states_table[tree.log] = tree.tree_size
            else:
                await states_topic.send(value={'log': tree.log, 'old_size':states_table[tree.log],
                    'diff': tree.tree_size-states_table[tree.log], 'tree_size':tree.tree_size})