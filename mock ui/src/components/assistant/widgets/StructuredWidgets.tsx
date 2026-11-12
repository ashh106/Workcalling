import { useState } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Checkbox } from "@/components/ui/checkbox";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { Slider } from "@/components/ui/slider";
import { Button } from "@/components/ui/button";
import { Check } from "lucide-react";

const Wrap = ({ title, children }: any) => (
  <div className="rounded-2xl bg-[hsl(var(--surface-input))] p-4 border border-[hsl(var(--surface-border))]">
    {title && <div className="text-xs font-medium text-[hsl(var(--surface-foreground))]/70 mb-3">{title}</div>}
    {children}
  </div>
);

/* TABS WIDGET
data: { tabs: [{ id, label, content: AssistantBlock[] | string, kpis?: [{label,value,delta?}] }] }
*/
export function TabsW({ title, data }: any) {
  const tabs = data.tabs || [];
  return (
    <Wrap title={title}>
      <Tabs defaultValue={tabs[0]?.id}>
        <TabsList className="bg-transparent border-b border-[hsl(var(--surface-border))] rounded-none w-full justify-start gap-1 h-auto p-0">
          {tabs.map((t: any) => (
            <TabsTrigger
              key={t.id}
              value={t.id}
              className="rounded-none border-b-2 border-transparent data-[state=active]:border-[hsl(var(--primary))] data-[state=active]:bg-transparent data-[state=active]:shadow-none px-3 py-2 text-sm"
            >
              {t.label}
            </TabsTrigger>
          ))}
        </TabsList>
        {tabs.map((t: any) => (
          <TabsContent key={t.id} value={t.id} className="pt-4 space-y-3">
            {t.kpis && (
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                {t.kpis.map((k: any) => (
                  <div key={k.label} className="rounded-xl bg-[hsl(var(--surface-muted))] p-3">
                    <div className="text-[11px] opacity-60">{k.label}</div>
                    <div className="text-lg font-semibold">{k.value}</div>
                    {k.delta && <div className="text-xs text-[hsl(var(--primary-glow))]">{k.delta}</div>}
                  </div>
                ))}
              </div>
            )}
            {t.rows && (
              <ul className="divide-y divide-[hsl(var(--surface-border))]">
                {t.rows.map((r: any, i: number) => (
                  <li key={i} className="flex items-center justify-between py-2 text-sm">
                    <span>{r.label}</span>
                    <span className="opacity-70">{r.value}</span>
                  </li>
                ))}
              </ul>
            )}
            {t.text && <p className="text-sm leading-relaxed opacity-80">{t.text}</p>}
          </TabsContent>
        ))}
      </Tabs>
    </Wrap>
  );
}

/* FORM WIDGET
data: {
  fields: [{ name, label, type: 'text'|'email'|'textarea'|'select'|'radio'|'checkbox'|'switch'|'slider', placeholder?, options?, required?, min?, max? }],
  submitLabel?, cancelLabel?
}
*/
export function FormW({ title, data }: any) {
  const fields = data.fields || [];
  const [values, setValues] = useState<Record<string, any>>(() =>
    Object.fromEntries(fields.map((f: any) => [f.name, f.type === "checkbox" ? [] : f.type === "switch" ? false : f.type === "slider" ? (f.min ?? 0) : ""]))
  );
  const [submitted, setSubmitted] = useState<null | Record<string, any>>(null);

  const set = (name: string, v: any) => setValues((s) => ({ ...s, [name]: v }));

  if (submitted) {
    return (
      <Wrap title={title}>
        <div className="flex items-start gap-3 py-2">
          <div className="size-8 rounded-full orb-gradient flex items-center justify-center shrink-0">
            <Check size={16} className="text-primary-foreground" />
          </div>
          <div className="space-y-1">
            <div className="text-sm font-medium">Submitted</div>
            <div className="text-xs opacity-70">Thanks — I've recorded your response.</div>
            <button onClick={() => setSubmitted(null)} className="text-xs underline opacity-70 hover:opacity-100 mt-1">Edit</button>
          </div>
        </div>
      </Wrap>
    );
  }

  return (
    <Wrap title={title}>
      <form
        onSubmit={(e) => { e.preventDefault(); setSubmitted(values); }}
        className="space-y-4"
      >
        {fields.map((f: any) => (
          <div key={f.name} className="space-y-1.5">
            <Label className="text-xs">{f.label}{f.required && <span className="text-destructive ml-0.5">*</span>}</Label>

            {(f.type === "text" || f.type === "email") && (
              <Input
                type={f.type}
                required={f.required}
                placeholder={f.placeholder}
                value={values[f.name]}
                onChange={(e) => set(f.name, e.target.value)}
                maxLength={255}
              />
            )}

            {f.type === "textarea" && (
              <Textarea
                required={f.required}
                placeholder={f.placeholder}
                value={values[f.name]}
                onChange={(e) => set(f.name, e.target.value)}
                maxLength={1000}
                rows={3}
              />
            )}

            {f.type === "select" && (
              <Select value={values[f.name]} onValueChange={(v) => set(f.name, v)}>
                <SelectTrigger><SelectValue placeholder={f.placeholder || "Select…"} /></SelectTrigger>
                <SelectContent>
                  {f.options.map((o: any) => (
                    <SelectItem key={o.value} value={o.value}>{o.label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            )}

            {f.type === "radio" && (
              <RadioGroup value={values[f.name]} onValueChange={(v) => set(f.name, v)} className="flex flex-wrap gap-3">
                {f.options.map((o: any) => (
                  <label key={o.value} className="flex items-center gap-2 text-sm cursor-pointer">
                    <RadioGroupItem value={o.value} id={`${f.name}-${o.value}`} />
                    <span>{o.label}</span>
                  </label>
                ))}
              </RadioGroup>
            )}

            {f.type === "checkbox" && (
              <div className="flex flex-wrap gap-3">
                {f.options.map((o: any) => {
                  const arr: string[] = values[f.name] || [];
                  const checked = arr.includes(o.value);
                  return (
                    <label key={o.value} className="flex items-center gap-2 text-sm cursor-pointer">
                      <Checkbox
                        checked={checked}
                        onCheckedChange={(c) =>
                          set(f.name, c ? [...arr, o.value] : arr.filter((x) => x !== o.value))
                        }
                      />
                      <span>{o.label}</span>
                    </label>
                  );
                })}
              </div>
            )}

            {f.type === "switch" && (
              <div className="flex items-center gap-3">
                <Switch checked={values[f.name]} onCheckedChange={(v) => set(f.name, v)} />
                <span className="text-xs opacity-70">{values[f.name] ? "On" : "Off"}</span>
              </div>
            )}

            {f.type === "slider" && (
              <div className="space-y-1">
                <Slider
                  value={[values[f.name]]}
                  min={f.min ?? 0}
                  max={f.max ?? 100}
                  step={f.step ?? 1}
                  onValueChange={(v) => set(f.name, v[0])}
                />
                <div className="text-xs opacity-60 text-right">{values[f.name]}</div>
              </div>
            )}
          </div>
        ))}

        <div className="flex gap-2 pt-1">
          <Button type="submit" className="flex-1">{data.submitLabel || "Submit"}</Button>
          <Button type="button" variant="outline" className="flex-1" onClick={() =>
            setValues(Object.fromEntries(fields.map((f: any) => [f.name, f.type === "checkbox" ? [] : f.type === "switch" ? false : f.type === "slider" ? (f.min ?? 0) : ""])))
          }>
            {data.cancelLabel || "Cancel"}
          </Button>
        </div>
      </form>
    </Wrap>
  );
}
