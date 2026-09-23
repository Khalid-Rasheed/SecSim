<template>
  <div class="max-w-6xl mx-auto px-4 py-10">
    <p class="eyebrow mb-2"><i class="fa-solid fa-flask me-2"></i>{{ $t('sim.title') }}</p>
    <h1 class="font-display text-3xl font-bold mb-1">{{ $t('sim.title') }}</h1>
    <p class="text-muted text-sm mb-6">{{ $t('sim.subtitle') }}</p>

    <!-- SELECTED ALGORITHM MASTHEAD -->
    <div class="panel px-6 py-5 mb-4 flex items-center gap-4 flex-wrap">
      <span
        class="w-14 h-14 rounded-2xl bg-cipher/10 border border-cipher/30 flex items-center justify-center shrink-0"
      >
        <i :class="[algoIcon(store.currentMeta?.type || 'encryption'), 'text-cipher text-2xl']"></i>
      </span>
      <div class="flex-1 min-w-[200px]">
        <p class="eyebrow mb-1">{{ $t('sim.now_simulating') }}</p>
        <h2 class="font-display font-bold text-3xl md:text-4xl tracking-tight leading-none">
          {{ store.currentMeta?.name?.[locale] || store.currentMeta?.name?.en || store.algorithm }}
        </h2>
        <p class="text-xs text-muted mt-1.5">
          <i class="fa-solid fa-circle-info me-1"></i>{{ $t('ux.tabs_desc.' + tabForAlgorithm(store.algorithm)) }}
        </p>
      </div>
      <span
        class="font-mono text-xs px-3 py-1.5 rounded-lg bg-cipher/10 border border-cipher/30 text-cipher"
        dir="ltr"
      >
        {{ taxBreadcrumb }}
      </span>
    </div>

    <div class="grid lg:grid-cols-5 gap-4 items-start">
      <!-- CONTROL DECK -->
      <div class="panel p-5 space-y-5 lg:col-span-2">
        <div>
          <h2 class="text-sm font-semibold mb-3">
            <i class="fa-solid fa-microchip text-cipher me-2"></i>{{ $t('sim.choose') }}
          </h2>
          <p class="text-[0.7rem] text-muted mb-2">{{ $t('tax.tabs_title') }}</p>
          <!-- TOP TABS: symmetric | asymmetric | hashing (+ attack lab) -->
          <div class="grid grid-cols-4 gap-1.5 mb-4" role="tablist">
            <button
              v-for="tab in tabs"
              :key="tab.key"
              role="tab"
              :aria-selected="activeTab === tab.key"
              :class="[
                'py-2 px-1 rounded-xl text-[0.7rem] font-bold border transition',
                activeTab === tab.key
                  ? 'bg-cipher/10 border-cipher text-cipher'
                  : 'bg-panel2 border-[rgba(148,163,184,0.16)] text-muted hover:border-muted'
              ]"
              @click="activeTab = tab.key"
            >
              <i :class="[tab.icon, 'mb-1 block']"></i>{{ tab.title }}
            </button>
          </div>
          <p class="text-[0.7rem] text-muted mb-4">
            <i class="fa-solid fa-circle-info me-1"></i>{{ $t('ux.tabs_desc.' + activeTab) }}
          </p>
          <!-- Groups inside the active tab: one section per kind -->
          <div class="space-y-4">
            <div v-for="grp in pickerGroups" :key="grp.key">
              <p class="text-[0.7rem] font-extrabold text-mist mb-1.5">
                {{ grp.title }}
                <span v-if="grp.sub" class="font-semibold text-muted">· {{ grp.sub }}</span>
              </p>
              <div class="grid grid-cols-2 gap-2">
                <button
                  v-for="a in grp.items"
                  :key="a.id"
                  :class="[
                    'panel-flat p-3 text-start transition',
                    store.algorithm === a.id ? '!border-cipher bg-cipher/10' : 'hover:border-muted'
                  ]"
                  @click="store.algorithm = a.id"
                >
                  <i
                    :class="[
                      algoIcon(a.type),
                      'text-xs mb-1.5',
                      store.algorithm === a.id ? 'text-cipher' : 'text-muted'
                    ]"
                  ></i>
                  <div class="font-display font-semibold text-sm">{{ displayName(a) }}</div>
                  <div class="flex gap-1 flex-wrap mt-1 items-center" dir="ltr">
                    <span class="text-[0.65rem] text-muted font-mono">{{ a.id }}</span>
                    <span
                      :class="[
                        'font-mono text-[0.6rem] px-1.5 py-px rounded border inline-flex items-center gap-1',
                        levelBadgeClasses(levelFor(a))
                      ]"
                      ><i :class="[levelIcon(levelFor(a))]"></i
                      >{{ $t('ux.level_' + levelFor(a)) }}</span
                    >
                    <span
                      v-if="a.security"
                      :class="[
                        'font-mono text-[0.6rem] px-1.5 py-px rounded border',
                        securityClass(a.security)
                      ]"
                      >{{ $t('alg.badge_' + a.security) }}</span
                    >
                  </div>
                </button>
              </div>
            </div>
          </div>
          <router-link
            :to="'/algorithms/' + store.algorithm"
            class="text-xs text-cipher hover:underline mt-2 inline-block"
          >
            <i class="fa-solid fa-book-open me-1"></i>{{ $t('alg.learn_more') }}:
            <span class="font-mono" dir="ltr">{{ store.algorithm }}</span>
          </router-link>
        </div>

        <!-- ALGORITHM BRIEF -->
        <div v-if="store.currentMeta" class="panel-flat p-4">
          <div class="flex items-center gap-2 mb-2">
            <i :class="[algoIcon(store.currentMeta.type), 'text-cipher text-sm']"></i>
            <h2 class="text-sm font-semibold">{{ $t('sim.brief') }}</h2>
            <span
              class="ms-auto font-mono text-[0.65rem] px-2 py-0.5 rounded bg-cipher/10 border border-cipher/30 text-cipher"
              dir="ltr"
            >
              {{ store.currentMeta.type }}
            </span>
          </div>
          <p v-if="briefText" class="text-xs text-mist/90 leading-relaxed line-clamp-3 mb-2">
            {{ briefText }}
          </p>
          <p v-else class="text-xs text-muted mb-2">
            <i class="fa-solid fa-circle-notch fa-spin me-1"></i>{{ $t('sim.brief_loading') }}
          </p>
          <div v-if="store.currentMeta.complexity" class="flex gap-1.5 flex-wrap mb-3" dir="ltr">
            <span
              class="font-mono text-[0.65rem] px-2 py-0.5 rounded bg-cipher/10 border border-cipher/30 text-cipher"
              >T: {{ store.currentMeta.complexity.time }}</span
            >
            <span
              class="font-mono text-[0.65rem] px-2 py-0.5 rounded bg-keyamber/10 border border-keyamber/30 text-keyamber"
              >S: {{ store.currentMeta.complexity.space }}</span
            >
          </div>
          <div class="flex gap-2">
            <button
              :disabled="store.loading"
              class="btn-ghost flex-1 py-2 text-xs disabled:opacity-50"
              @click="store.fillExample()"
            >
              <i class="fa-solid fa-wand-magic-sparkles me-1.5"></i>{{ $t('sim.example') }}
            </button>
            <router-link
              :to="'/algorithms/' + store.algorithm"
              class="btn-ghost flex-1 py-2 text-xs text-center"
            >
              <i class="fa-solid fa-book-open me-1.5"></i>{{ $t('alg.learn_more') }}
            </router-link>
          </div>
        </div>

        <div class="hairline-t pt-5">
          <h2 class="text-sm font-semibold mb-3">
            <i class="fa-solid fa-keyboard text-cipher me-2"></i>{{ $t('sim.input') }}
          </h2>
          <label class="block text-xs text-muted mb-1.5">{{ $t('sim.text') }}<FieldHint tip-key="text" /></label>
          <input
            v-model="store.input"
            class="field w-full px-3 py-2.5 text-sm font-mono mb-1"
            dir="ltr"
            placeholder="Hello World"
            @keyup.enter="store.run()"
          />
          <p v-if="store.algorithm === 'brute_force'" class="text-[0.7rem] text-keyamber mb-4">
            <i class="fa-solid fa-burst me-1"></i>{{ $t('sim.attack_hint') }}
          </p>
          <p v-else-if="store.algorithm === 'vigenere_breaker'" class="text-[0.7rem] text-keyamber mb-4">
            <i class="fa-solid fa-burst me-1"></i>{{ $t('sim.breaker_hint') }}
          </p>
          <p v-else-if="store.algorithm === 'dh_mitm'" class="text-[0.7rem] text-keyamber mb-4">
            <i class="fa-solid fa-burst me-1"></i>{{ $t('sim.mitm_hint') }}
          </p>
          <p v-else-if="store.algorithm === 'birthday_collision'" class="text-[0.7rem] text-keyamber mb-4">
            <i class="fa-solid fa-burst me-1"></i>{{ $t('sim.collision_hint') }}
          </p>
          <p v-else-if="store.algorithm === 'dictionary_attack'" class="text-[0.7rem] text-keyamber mb-4">
            <i class="fa-solid fa-burst me-1"></i>{{ $t('sim.dict_hint') }}
          </p>
          <p
            v-else-if="store.algorithm === 'rsa' && store.mode === 'decrypt'"
            class="text-[0.7rem] text-keyamber mb-4"
          >
            <i class="fa-solid fa-circle-info me-1"></i>{{ $t('sim.rsa_decrypt_hint') }}
          </p>
          <p v-else-if="store.algorithm === 'rsa'" class="text-[0.7rem] text-muted mb-4">
            <i class="fa-solid fa-circle-info me-1"></i>{{ $t('sim.rsa_hint') }}
          </p>
          <p v-else-if="store.algorithm === 'diffie_hellman'" class="text-[0.7rem] text-muted mb-4">
            <i class="fa-solid fa-circle-info me-1"></i>{{ $t('sim.dh_note') }}
          </p>
          <p v-else-if="store.algorithm === 'elgamal'" class="text-[0.7rem] text-muted mb-4">
            <i class="fa-solid fa-circle-info me-1"></i>{{ $t('sim.elgamal_note') }}
          </p>
          <p v-else-if="store.algorithm === 'playfair'" class="text-[0.7rem] text-muted mb-4">
            <i class="fa-solid fa-circle-info me-1"></i>{{ $t('sim.playfair_note') }}
          </p>
          <div v-else class="mb-4"></div>
          <div v-if="store.algorithm === 'caesar'" class="mb-4">
            <label class="block text-xs text-muted mb-1.5">{{ $t('sim.key') }}<FieldHint tip-key="key" /></label>
            <input
              v-model.number="store.key"
              type="number"
              min="0"
              max="25"
              class="field w-full px-3 py-2.5 text-sm font-mono"
              dir="ltr"
            />
          </div>
          <div v-if="store.algorithm === 'vigenere'" class="mb-4">
            <label class="block text-xs text-muted mb-1.5">{{ $t('sim.vigenere_key') }}<FieldHint tip-key="vigenere_key" /></label>
            <input
              v-model="store.vigenereKey"
              class="field w-full px-3 py-2.5 text-sm font-mono"
              dir="ltr"
              placeholder="LEMON"
            />
          </div>
          <div v-if="store.algorithm === 'playfair'" class="mb-4">
            <label class="block text-xs text-muted mb-1.5">{{ $t('sim.playfair_key') }}<FieldHint tip-key="playfair_key" /></label>
            <input
              v-model="store.playfairKey"
              class="field w-full px-3 py-2.5 text-sm font-mono"
              dir="ltr"
              placeholder="MONARCHY"
            />
          </div>
          <div v-if="store.algorithm === 'rc4'" class="mb-4">
            <label class="block text-xs text-muted mb-1.5">{{ $t('sim.rc4_key') }}<FieldHint tip-key="rc4_key" /></label>
            <input
              v-model="store.rc4Key"
              class="field w-full px-3 py-2.5 text-sm font-mono"
              dir="ltr"
              placeholder="secret"
            />
          </div>
          <div
            v-if="['caesar', 'vigenere', 'playfair', 'rc4', 'aes', 'rsa', 'elgamal'].includes(store.algorithm)"
            class="mb-4"
          >
            <label class="block text-xs text-muted mb-1.5">{{ $t('sim.mode') }}<FieldHint tip-key="mode" /></label>
            <select v-model="store.mode" class="field w-full px-3 py-2.5 text-sm">
              <option value="encrypt">{{ $t('sim.encrypt') }}</option>
              <option value="decrypt">{{ $t('sim.decrypt') }}</option>
            </select>
          </div>
          <div v-if="store.algorithm === 'aes'" class="grid grid-cols-2 gap-3 mb-4">
            <div class="col-span-2">
              <label class="block text-xs text-muted mb-1.5">{{ $t('sim.key_text') }}<FieldHint tip-key="key_text" /></label>
              <input
                v-model="store.aesKeyText"
                class="field w-full px-3 py-2.5 text-sm font-mono"
                dir="ltr"
              />
            </div>
            <div class="col-span-2">
              <label class="block text-xs text-muted mb-1.5">{{ $t('sim.key_size') }}<FieldHint tip-key="key_size" /></label>
              <select
                v-model.number="store.aesKeySize"
                class="field w-full px-3 py-2.5 text-sm font-mono"
                dir="ltr"
              >
                <option :value="128">128</option>
                <option :value="192">192</option>
                <option :value="256">256</option>
              </select>
            </div>
          </div>
          <div v-if="store.algorithm === 'rsa'" class="grid grid-cols-3 gap-3 mb-4">
            <div>
              <label class="block text-xs text-muted mb-1.5" dir="ltr">p<FieldHint tip-key="rsa_p" /></label>
              <input
                v-model.number="store.rsaP"
                type="number"
                class="field w-full px-3 py-2.5 text-sm font-mono"
                dir="ltr"
              />
            </div>
            <div>
              <label class="block text-xs text-muted mb-1.5" dir="ltr">q<FieldHint tip-key="rsa_q" /></label>
              <input
                v-model.number="store.rsaQ"
                type="number"
                class="field w-full px-3 py-2.5 text-sm font-mono"
                dir="ltr"
              />
            </div>
            <div>
              <label class="block text-xs text-muted mb-1.5" dir="ltr">e<FieldHint tip-key="rsa_e" /></label>
              <input
                v-model.number="store.rsaE"
                type="number"
                class="field w-full px-3 py-2.5 text-sm font-mono"
                dir="ltr"
              />
            </div>
          </div>
          <div v-if="store.algorithm === 'diffie_hellman'" class="grid grid-cols-2 gap-3 mb-4">
            <div>
              <label class="block text-xs text-muted mb-1.5" dir="ltr">p<FieldHint tip-key="dh_p" /></label>
              <input
                v-model.number="store.dhP"
                type="number"
                class="field w-full px-3 py-2.5 text-sm font-mono"
                dir="ltr"
              />
            </div>
            <div>
              <label class="block text-xs text-muted mb-1.5" dir="ltr">g<FieldHint tip-key="dh_g" /></label>
              <input
                v-model.number="store.dhG"
                type="number"
                class="field w-full px-3 py-2.5 text-sm font-mono"
                dir="ltr"
              />
            </div>
            <div>
              <label class="block text-xs text-muted mb-1.5">{{ $t('sim.dh_a') }}<FieldHint tip-key="dh_a" /></label>
              <input
                v-model.number="store.dhA"
                type="number"
                class="field w-full px-3 py-2.5 text-sm font-mono"
                dir="ltr"
              />
            </div>
            <div>
              <label class="block text-xs text-muted mb-1.5">{{ $t('sim.dh_b') }}<FieldHint tip-key="dh_b" /></label>
              <input
                v-model.number="store.dhB"
                type="number"
                class="field w-full px-3 py-2.5 text-sm font-mono"
                dir="ltr"
              />
            </div>
          </div>
          <div v-if="store.algorithm === 'dh_mitm'" class="grid grid-cols-2 gap-3 mb-4">
            <div>
              <label class="block text-xs text-muted mb-1.5" dir="ltr">p<FieldHint tip-key="dh_p" /></label>
              <input
                v-model.number="store.dhP"
                type="number"
                class="field w-full px-3 py-2.5 text-sm font-mono"
                dir="ltr"
              />
            </div>
            <div>
              <label class="block text-xs text-muted mb-1.5" dir="ltr">g<FieldHint tip-key="dh_g" /></label>
              <input
                v-model.number="store.dhG"
                type="number"
                class="field w-full px-3 py-2.5 text-sm font-mono"
                dir="ltr"
              />
            </div>
            <div>
              <label class="block text-xs text-muted mb-1.5">{{ $t('sim.dh_a') }}<FieldHint tip-key="dh_a" /></label>
              <input
                v-model.number="store.dhA"
                type="number"
                class="field w-full px-3 py-2.5 text-sm font-mono"
                dir="ltr"
              />
            </div>
            <div>
              <label class="block text-xs text-muted mb-1.5">{{ $t('sim.dh_b') }}<FieldHint tip-key="dh_b" /></label>
              <input
                v-model.number="store.dhB"
                type="number"
                class="field w-full px-3 py-2.5 text-sm font-mono"
                dir="ltr"
              />
            </div>
            <div>
              <label class="block text-xs text-muted mb-1.5">{{ $t('sim.mitm_e') }}<FieldHint tip-key="mitm_e" /></label>
              <input
                v-model.number="store.mitmE"
                type="number"
                class="field w-full px-3 py-2.5 text-sm font-mono"
                dir="ltr"
              />
            </div>
            <div>
              <label class="block text-xs text-muted mb-1.5">{{ $t('sim.mitm_f') }}<FieldHint tip-key="mitm_f" /></label>
              <input
                v-model.number="store.mitmF"
                type="number"
                class="field w-full px-3 py-2.5 text-sm font-mono"
                dir="ltr"
              />
            </div>
          </div>
          <div v-if="store.algorithm === 'birthday_collision'" class="mb-4">
            <label class="block text-xs text-muted mb-1.5">{{ $t('sim.collision_bits') }}<FieldHint tip-key="collision_bits" /></label>
            <input
              v-model.number="store.collisionBits"
              type="number"
              min="8"
              max="24"
              class="field w-full px-3 py-2.5 text-sm font-mono"
              dir="ltr"
            />
          </div>
          <div v-if="store.algorithm === 'elgamal'" class="grid grid-cols-2 gap-3 mb-4">
            <div>
              <label class="block text-xs text-muted mb-1.5" dir="ltr">p<FieldHint tip-key="elgamal_p" /></label>
              <input
                v-model.number="store.elgamalP"
                type="number"
                class="field w-full px-3 py-2.5 text-sm font-mono"
                dir="ltr"
              />
            </div>
            <div>
              <label class="block text-xs text-muted mb-1.5" dir="ltr">g<FieldHint tip-key="elgamal_g" /></label>
              <input
                v-model.number="store.elgamalG"
                type="number"
                class="field w-full px-3 py-2.5 text-sm font-mono"
                dir="ltr"
              />
            </div>
            <div>
              <label class="block text-xs text-muted mb-1.5">{{ $t('sim.elgamal_x') }}<FieldHint tip-key="elgamal_x" /></label>
              <input
                v-model.number="store.elgamalX"
                type="number"
                class="field w-full px-3 py-2.5 text-sm font-mono"
                dir="ltr"
              />
            </div>
            <div>
              <label class="block text-xs text-muted mb-1.5">{{ $t('sim.elgamal_k') }}<FieldHint tip-key="elgamal_k" /></label>
              <input
                v-model.number="store.elgamalK"
                type="number"
                class="field w-full px-3 py-2.5 text-sm font-mono"
                dir="ltr"
              />
            </div>
          </div>
          <div v-if="store.algorithm === 'pbkdf2'" class="grid grid-cols-2 gap-3 mb-4">
            <div class="col-span-2">
              <label class="block text-xs text-muted mb-1.5">{{ $t('sim.pbkdf2_salt') }}<FieldHint tip-key="pbkdf2_salt" /></label>
              <input
                v-model="store.pbkdf2Salt"
                class="field w-full px-3 py-2.5 text-sm font-mono"
                dir="ltr"
                placeholder="empty = random"
              />
            </div>
            <div class="col-span-2">
              <label class="block text-xs text-muted mb-1.5">{{ $t('sim.pbkdf2_iterations') }}<FieldHint tip-key="pbkdf2_iterations" /></label>
              <input
                v-model.number="store.pbkdf2Iterations"
                type="number"
                min="1"
                max="2000000"
                class="field w-full px-3 py-2.5 text-sm font-mono"
                dir="ltr"
              />
            </div>
          </div>
          <button
            :disabled="store.loading"
            class="btn-cipher w-full py-3 text-sm disabled:opacity-50"
            @click="store.run()"
          >
            <i v-if="store.loading" class="fa-solid fa-circle-notch fa-spin me-2"></i>
            <i v-else class="fa-solid fa-play me-2"></i>{{ $t('sim.run') }}
          </button>
          <p v-if="store.error" class="text-dangerx text-xs mt-2">
            <i class="fa-solid fa-triangle-exclamation me-1"></i>{{ store.error }}
          </p>
        </div>
      </div>

      <!-- TERMINAL -->
      <div class="lg:col-span-3 space-y-4">
        <div class="panel p-5">
          <div class="flex items-center gap-1.5 mb-4" dir="ltr">
            <span class="w-2.5 h-2.5 rounded-full bg-dangerx/80"></span>
            <span class="w-2.5 h-2.5 rounded-full bg-keyamber/80"></span>
            <span class="w-2.5 h-2.5 rounded-full bg-cipher/80"></span>
            <span class="ms-2 font-mono text-xs text-muted">secsim — {{ store.algorithm }}</span>
          </div>
          <div v-if="store.result" class="panel-flat p-4 mb-1">
            <div class="flex items-center justify-between mb-1.5">
              <p class="text-xs text-muted">{{ $t('sim.result') }}</p>
              <button class="btn-ghost px-2 py-1 text-[0.7rem]" @click="copyResult()">
                <i :class="['me-1', copied ? 'fa-solid fa-check text-cipher' : 'fa-solid fa-copy']"></i
                >{{ copied ? $t('sim.copied') : $t('sim.copy') }}
              </button>
            </div>
            <p class="font-mono text-cipher break-all" dir="ltr">{{ store.result }}</p>
          </div>
          <div
            v-if="store.warning"
            class="flex items-start gap-2 bg-amber-50 border border-amber-300 text-amber-800 text-xs font-semibold rounded-xl px-3.5 py-3 mt-3"
          >
            <i class="fa-solid fa-triangle-exclamation mt-0.5 shrink-0"></i>
            <span>{{ store.warning[locale] || store.warning.en }}</span>
          </div>
          <p v-if="!store.result" class="text-sm text-muted">
            <i class="fa-solid fa-terminal me-2"></i>{{ $t('sim.need_run') }}
          </p>
        </div>

        <VisualizationArea v-if="store.steps.length" />
        <SecurityMetrics v-if="store.analysis" />
        <ComparePanel />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useSimulationStore } from '../stores/simulationStore'
import VisualizationArea from '../components/simulation/VisualizationArea.vue'
import SecurityMetrics from '../components/analysis/SecurityMetrics.vue'
import ComparePanel from '../components/analysis/ComparePanel.vue'
import FieldHint from '../components/common/FieldHint.vue'
import { levelFor, levelBadgeClasses, levelIcon } from '../utils/ux'
const store = useSimulationStore()
const route = useRoute()
const { t, locale } = useI18n()
const copied = ref(false)
function algoIcon(type) {
  if (type === 'attack') return 'fa-solid fa-burst'
  if (type === 'hashing') return 'fa-solid fa-fingerprint'
  return 'fa-solid fa-key'
}
function securityClass(level) {
  if (level === 'secure') return 'bg-cipher/10 border-cipher/30 text-cipher'
  if (level === 'broken') return 'bg-dangerx/10 border-dangerx/30 text-dangerx'
  if (level === 'legacy') return 'bg-keyamber/10 border-keyamber/30 text-keyamber'
  return 'bg-panel2 border-[rgba(148,163,184,0.25)] text-muted'
}
// Breadcrumb for the masthead badge, e.g. "تناظرية · كلاسيكية".
// Family/kind keys are translated via tax.* (raw id as fallback).
const taxBreadcrumb = computed(() => {
  const m = store.currentMeta
  if (!m) return '—'
  const fam = m.family ? t('tax.' + m.family) : m.type
  if (m.family && m.kind) return `${fam} · ${t('tax.' + m.kind)}`
  return fam
})
/** Human display name for picker buttons (bilingual name, raw id fallback). */
function displayName(a) {
  return a.name?.[locale.value] || a.name?.en || a.id
}
// Top tabs: symmetric | asymmetric | hashing | attack lab.
const activeTab = ref('symmetric')
const tabs = computed(() => [
  { key: 'symmetric', title: t('tax.symmetric'), icon: 'fa-solid fa-key text-cipher' },
  { key: 'asymmetric', title: t('tax.asymmetric'), icon: 'fa-solid fa-key text-keyamber' },
  { key: 'hashing', title: t('tax.hashing'), icon: 'fa-solid fa-fingerprint text-cipher' },
  { key: 'attack', title: t('tax.attack_lab'), icon: 'fa-solid fa-burst text-dangerx' }
])
function tabForAlgorithm(id) {
  const m = store.algorithms.find((a) => a.id === id)
  if (!m) return 'symmetric'
  if (m.type === 'attack') return 'attack'
  if (m.family === 'asymmetric') return 'asymmetric'
  if (m.family === 'hashing') return 'hashing'
  return 'symmetric'
}
// Groups inside the active tab: one section per kind, preserving
// catalog order. Falls back to the flat list when taxonomy is missing.
const pickerGroups = computed(() => {
  const inTab =
    activeTab.value === 'attack'
      ? store.algorithms.filter((a) => a.type === 'attack')
      : store.algorithms.filter((a) => a.family === activeTab.value)
  const kinds = []
  for (const a of inTab) {
    if (!kinds.includes(a.kind)) kinds.push(a.kind)
  }
  return kinds.map((kind) => ({
    key: `${activeTab.value}/${kind || 'all'}`,
    title: t('tax.' + activeTab.value),
    sub: kind ? t('tax.' + kind) : '',
    items: inTab.filter((a) => a.kind === kind)
  }))
})
const briefText = computed(() => {
  const d = store.currentDetail?.details?.overview
  if (d) return d[locale.value] || d.en
  const m = store.currentMeta?.description
  return m ? m[locale.value] || m.en : ''
})
async function copyResult() {
  if (!store.result) return
  try {
    await navigator.clipboard.writeText(store.result)
  } catch {
    const ta = document.createElement('textarea')
    ta.value = store.result
    document.body.appendChild(ta)
    ta.select()
    document.execCommand('copy')
    ta.remove()
  }
  copied.value = true
  setTimeout(() => {
    copied.value = false
  }, 1500)
}
watch(
  () => store.algorithm,
  async (id) => {
    copied.value = false
    activeTab.value = tabForAlgorithm(id)
    await store.fetchDetails()
    if (store.input) await store.run()
  }
)
onMounted(async () => {
  try {
    await store.fetchAlgorithms()
  } catch {
    /* offline */
  }
  const preset = route.query.algo
  if (preset && store.algorithms.some((a) => a.id === preset)) store.algorithm = preset
  activeTab.value = tabForAlgorithm(store.algorithm)
  await store.fetchDetails()
  if (store.input && !store.result) await store.run()
})
// React to navbar-dropdown navigation while already on this view:
// /simulator?algo=aes must switch the bench without a full reload.
watch(
  () => route.query.algo,
  async (id) => {
    if (id && id !== store.algorithm && store.algorithms.some((a) => a.id === id)) {
      store.algorithm = id
    }
  }
)
</script>
