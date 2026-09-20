import ThemeSwitcher from "../components/ThemeSwitcher";
import FontSelector from "../components/FontSelector";
import StatsCard from "../components/StatsCard";
import Button from "../components/Button";
import { Coffee, IndianRupee, Users } from "lucide-react";

const Section = ({ title, description, children }) => (
  <section className="rounded-lg border border-border bg-surface p-6 space-y-4">
    <header className="space-y-1">
      <h2 className="text-lg font-semibold text-foreground">{title}</h2>
      {description && (
        <p className="text-sm text-muted-foreground">{description}</p>
      )}
    </header>
    {children}
  </section>
);

const AppSettings = () => (
  <div className="space-y-6 p-4 md:p-6">
    <header className="space-y-1">
      <h1 className="text-2xl font-bold text-foreground">Appearance</h1>
      <p className="text-sm text-muted-foreground">
        Changes apply immediately and are saved for everyone.
      </p>
    </header>

    <Section
      title="Theme"
      description="Pick the colour scheme your staff will look at all day. Every theme is contrast-checked, so labels stay readable on buttons."
    >
      <ThemeSwitcher />
    </Section>

    <Section
      title="Typography"
      description="The typeface used across the whole app."
    >
      <FontSelector />
    </Section>

    <Section
      title="Preview"
      description="The components below use the same tokens as the rest of the app, so this is what your choice actually looks like."
    >
      <div className="grid gap-4 sm:grid-cols-3">
        <StatsCard
          label="Today's sales"
          value={"₹18,420"}
          description="32 bills"
          icon={IndianRupee}
        />
        <StatsCard
          label="Covers"
          value="128"
          description="Across 14 tables"
          icon={Coffee}
        />
        <StatsCard
          label="On shift"
          value="6"
          description="2 on break"
          icon={Users}
        />
      </div>

      <div className="flex flex-wrap gap-2 pt-2">
        <Button label="Primary" />
        <Button label="Secondary" variant="secondary" />
        <Button label="Outline" variant="outline" />
        <Button label="Delete" variant="danger" />
      </div>
    </Section>
  </div>
);

export default AppSettings;
