def _javac_params(target, ctx):
    params = []
    for action in target.actions:
        if not action.mnemonic == "Javac" and not action.mnemonic == "KotlinCompile":
            continue
        output = ctx.actions.declare_file("%s.javac_params" % target.label.name)
        args = ctx.actions.args()
        args.add_all(action.argv)
        ctx.actions.write(
            output = output,
            content = args,
        )
        params.append(output)
        break
    return [OutputGroupInfo(unused_deps_outputs = depset(params))]

javac_params = aspect(
    implementation = _javac_params,
)
