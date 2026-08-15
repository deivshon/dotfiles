import { Command } from "commander"
import { z } from "zod"

const optionsSchema = z.object({
    dryRun: z.boolean(),
})

export type CliOptions = z.infer<typeof optionsSchema>

/**
 * @param argv Arguments to read
 * @description Reads the command line arguments of the process.
 */
export const parseCliOptions = (argv: string[]): CliOptions =>
    optionsSchema.parse(
        new Command()
            .name("dotfiles")
            .description("Installs the applications of this machine")
            .option("--dry-run", "Show the plan without running any install", false)
            .parse(argv)
            .opts(),
    )
