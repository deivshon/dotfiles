import { exit } from "node:process"

import { Command } from "commander"
import { kebabCase } from "es-toolkit"
import { colors } from "es-toolkit/server"
import { z } from "zod"

const optionsSchema = z.object({
    dryRun: z.stringbool(),
    configs: z.stringbool(),
})

export type CliOptions = z.infer<typeof optionsSchema>

/**
 * @param path Path of the value in the schema
 * @description Returns the flag that carries the value.
 */
const flagOf = (path: PropertyKey[]): string =>
    `--${path.map(key => kebabCase(String(key))).join(".")}`

/**
 * @param argv Arguments to read
 * @description Reads the command line arguments of the process.
 * @remarks Ends the process when a flag carries a value that is not a boolean.
 */
export const parseCliOptions = (argv: string[]): CliOptions => {
    const options = optionsSchema.safeParse(
        new Command()
            .name("dotfiles")
            .description("Installs the applications of this machine")
            .option(
                "--dry-run <enabled>",
                "Show the plan without running any install",
                "false",
            )
            .option("--configs <enabled>", "Copy the config files", "true")
            .parse(argv)
            .opts(),
    )
    if (options.success) {
        return options.data
    }

    console.error(
        colors.red(
            options.error.issues
                .map(issue => `The flag ${flagOf(issue.path)} takes true or false`)
                .join("\n"),
        ),
    )
    return exit(1)
}
