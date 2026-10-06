"""Author menu translations as data; no runtime translation service."""
from pathlib import Path
import json
R=Path(__file__).resolve().parent
keys=['mode','normal','enhanced','strategy','block_perf','mode_description','keys_description','perf_description','hint','seat1','seat2','seat3','seat4','seat5']
rows={
'en':[
 'Variant','Normal','Enhanced','Key strategy','Block performance monitor hotkeys',
 'Normal uses native seat groups. Enhanced also switches across groups in solo and multiplayer. Changes apply after the current switch finishes.',
 'INI and menu bindings are independent. Menu bindings start unbound: assign them on the MODS binding tab. Switching strategy never overwrites either configuration.',
 'Block F2-F5 performance monitor shortcuts. Seat bindings keep working. Off by default.',
 'INI active. Set Key strategy to ModBindingsMenu to use these bindings.',
 'Seat 1: Driver','Seat 2: Front passenger / Gunner','Seat 3: Rear left / Left passenger / Flamer','Seat 4: Rear right / Right passenger','Seat 5: M-102 machine gunner'],
'zh-Hans':[
 '版本选择','普通版','加强版','按键策略','游戏内性能监控屏蔽',
 '普通版保留原有座位分组；加强版支持单人、多人跨区换座。当前换座完成后应用新设置。',
 'INI 与菜单按键独立保存、互不覆盖。菜单按键初始未绑定，请到 MODS 按键页设置。可随时切换生效来源。',
 '屏蔽 F2–F5 调整游戏性能监控的快捷键，保留换座按键。默认关闭。',
 '当前生效的为VehicleSeatSwitch.ini配置，若要使用下列设置请将“按键策略”改为“ModBindingsMenu”。',
 '座位1：驾驶位','座位2：副驾／炮位','座位3：后左／左乘员／喷火','座位4：后右／右乘员','座位5：M-102机枪位'],
'zh-Hant':[
 '版本選擇','普通版','加強版','按鍵策略','遊戲內效能監控屏蔽',
 '普通版保留原有座位分組；加強版支援單人、多人跨區換座。目前換座完成後套用新設定。',
 'INI 與選單按鍵獨立儲存、互不覆寫。選單按鍵起初未綁定，請到 MODS 按鍵頁設定。可隨時切換生效來源。',
 '屏蔽 F2–F5 調整遊戲效能監控的快捷鍵，保留換座按鍵。預設關閉。',
 '目前使用VehicleSeatSwitch.ini設定；如要使用下列設定，請將「按鍵策略」改為「ModBindingsMenu」。',
 '座位1：駕駛位','座位2：副駕／炮位','座位3：後左／左乘員／噴火','座位4：後右／右乘員','座位5：M-102機槍位'],
'ja':[
 'バージョン選択','通常版','強化版','キー設定の選択','性能モニターのキーを無効化',
 '通常版は元の座席グループ内で移動します。強化版はソロとマルチでグループを越えて移動できます。座席移動の完了後に変更を適用します。',
 'INI とメニューの設定は独立しています。メニューの初期割り当ては空です。MODS キー設定で割り当ててください。切り替えても上書きしません。',
 'F2–F5 による性能モニター操作を無効にします。座席キーは使えます。初期設定はオフです。',
 'INI が有効です。この設定を使うには「キー設定の選択」を ModBindingsMenu に変更してください。',
 '座席1：運転席','座席2：助手席／砲手','座席3：左後部／左乗員／火炎放射器','座席4：右後部／右乗員','座席5：M-102 機銃手'],
'ko':[
 '버전 선택','일반판','강화판','키 설정 방식','성능 모니터 단축키 차단',
 '일반판은 기존 좌석 그룹을 유지합니다. 강화판은 싱글 및 멀티플레이에서 그룹 간 이동을 지원합니다. 현재 좌석 이동이 끝난 후 적용됩니다.',
 'INI와 메뉴 설정은 별도로 저장됩니다. 메뉴 키는 처음에 미지정 상태입니다. MODS 키 설정에서 지정하세요. 방식을 바꿔도 다른 설정을 덮어쓰지 않습니다.',
 'F2–F5 성능 모니터 단축키를 차단합니다. 좌석 키는 유지됩니다. 기본값은 끄기입니다.',
 'INI 사용 중입니다. 아래 설정을 사용하려면 키 설정 방식을 ModBindingsMenu로 바꾸세요.',
 '좌석 1: 운전석','좌석 2: 조수석 / 포수','좌석 3: 뒤 왼쪽 / 왼쪽 승객 / 화염방사기','좌석 4: 뒤 오른쪽 / 오른쪽 승객','좌석 5: M-102 기관총 사수'],
'fr':[
 'Version','Normale','Améliorée','Source des touches','Bloquer les touches du moniteur',
 'Normale conserve les groupes de sièges. Améliorée permet de changer de groupe en solo et en multijoueur. Les changements attendent la fin du déplacement en cours.',
 'Les réglages INI et du menu sont indépendants. Les touches du menu sont initialement libres : configurez-les dans MODS. Changer de source ne remplace aucun réglage.',
 'Bloque F2–F5 pour le moniteur de performances, sans bloquer les commandes de siège. Désactivé par défaut.',
 'INI actif. Choisissez ModBindingsMenu dans Source des touches pour utiliser ces réglages.',
 'Siège 1 : conducteur','Siège 2 : passager avant / tireur','Siège 3 : arrière gauche / passager gauche / lance-flammes','Siège 4 : arrière droit / passager droit','Siège 5 : mitrailleur du M-102'],
'de':[
 'Version','Normal','Erweitert','Tastenquelle','Leistungsanzeige-Tasten sperren',
 'Normal behält die Sitzgruppen des Spiels bei. Erweitert erlaubt Gruppenwechsel im Einzel- und Mehrspielermodus. Änderungen gelten nach dem laufenden Sitzwechsel.',
 'INI und Menü speichern ihre Belegung unabhängig. Menütasten sind anfangs unbelegt: im MODS-Reiter zuweisen. Ein Quellenwechsel überschreibt keine Belegung.',
 'Sperrt F2–F5 für die Leistungsanzeige. Sitztasten bleiben nutzbar. Standardmäßig aus.',
 'INI aktiv. Für diese Belegung Tastenquelle auf ModBindingsMenu stellen.',
 'Sitz 1: Fahrer','Sitz 2: Beifahrer / Schütze','Sitz 3: hinten links / linker Passagier / Flammenwerfer','Sitz 4: hinten rechts / rechter Passagier','Sitz 5: M-102-MG-Schütze'],
'it':[
 'Versione','Normale','Potenziata','Fonte dei tasti','Blocca tasti monitor prestazioni',
 'Normale mantiene i gruppi di posti originali. Potenziata permette di cambiare gruppo in singolo e multigiocatore. Le modifiche attendono la fine del cambio in corso.',
 'Le configurazioni INI e del menu sono indipendenti. I tasti del menu sono inizialmente liberi: assegnali nella scheda MODS. Cambiare fonte non sovrascrive nulla.',
 'Blocca F2–F5 per il monitor delle prestazioni, mantenendo i tasti dei posti. Disattivato per impostazione predefinita.',
 'INI attivo. Seleziona ModBindingsMenu come Fonte dei tasti per usare queste impostazioni.',
 'Posto 1: conducente','Posto 2: passeggero anteriore / artigliere','Posto 3: posteriore sinistro / passeggero sinistro / lanciafiamme','Posto 4: posteriore destro / passeggero destro','Posto 5: mitragliere M-102'],
'es':[
 'Versión','Normal','Mejorada','Origen de los controles','Bloquear teclas de rendimiento',
 'Normal mantiene los grupos de asientos originales. Mejorada permite cambiar entre grupos en solitario y multijugador. Los cambios se aplican al terminar el cambio de asiento actual.',
 'INI y menú guardan configuraciones independientes. Los controles del menú empiezan sin asignar: configúralos en MODS. Cambiar el origen no sobrescribe ninguna configuración.',
 'Bloquea F2–F5 para el monitor de rendimiento. Los controles de los asientos siguen funcionando. Desactivado por defecto.',
 'INI activo. Selecciona ModBindingsMenu en Origen de los controles para usar estos ajustes.',
 'Asiento 1: conductor','Asiento 2: copiloto / artillero','Asiento 3: trasero izquierdo / pasajero izquierdo / lanzallamas','Asiento 4: trasero derecho / pasajero derecho','Asiento 5: ametrallador del M-102'],
'es-419':[
 'Versión','Normal','Mejorada','Origen de los controles','Bloquear teclas de rendimiento',
 'Normal conserva los grupos de asientos originales. Mejorada permite cambiar entre grupos en solitario y multijugador. Los cambios se aplican al terminar el cambio de asiento actual.',
 'INI y menú guardan configuraciones independientes. Los controles del menú empiezan sin asignar: configúralos en MODS. Cambiar el origen no sobrescribe ninguna configuración.',
 'Bloquea F2–F5 para el monitor de rendimiento. Los controles de los asientos siguen funcionando. Desactivado de forma predeterminada.',
 'INI activo. Selecciona ModBindingsMenu en Origen de los controles para usar estos ajustes.',
 'Asiento 1: conductor','Asiento 2: copiloto / artillero','Asiento 3: trasero izquierdo / pasajero izquierdo / lanzallamas','Asiento 4: trasero derecho / pasajero derecho','Asiento 5: ametrallador del M-102'],
'pt-BR':[
 'Versão','Normal','Aprimorada','Origem das teclas','Bloquear teclas de desempenho',
 'Normal mantém os grupos de assentos originais. Aprimorada permite trocar entre grupos no modo solo e multijogador. As mudanças aguardam o fim da troca de assento atual.',
 'INI e menu salvam configurações independentes. As teclas do menu começam sem atribuição: configure-as em MODS. Trocar a origem não sobrescreve configurações.',
 'Bloqueia F2–F5 para o monitor de desempenho. As teclas dos assentos continuam funcionando. Desativado por padrão.',
 'INI ativo. Escolha ModBindingsMenu em Origem das teclas para usar estas configurações.',
 'Assento 1: motorista','Assento 2: passageiro dianteiro / artilheiro','Assento 3: traseiro esquerdo / passageiro esquerdo / lança-chamas','Assento 4: traseiro direito / passageiro direito','Assento 5: metralhador do M-102'],
'pl':[
 'Wersja','Zwykła','Rozszerzona','Źródło przypisań','Blokuj klawisze monitora wydajności',
 'Zwykła zachowuje grupy miejsc z gry. Rozszerzona pozwala zmieniać grupy w grze solo i wieloosobowej. Ustawienia zmienią się po zakończeniu bieżącej zmiany miejsca.',
 'INI i menu zapisują przypisania niezależnie. Klawisze menu są początkowo nieprzypisane: ustaw je w MODS. Zmiana źródła nie nadpisuje przypisań.',
 'Blokuje F2–F5 monitora wydajności. Klawisze miejsc nadal działają. Domyślnie wyłączone.',
 'INI aktywne. Wybierz ModBindingsMenu jako Źródło przypisań, aby użyć tych ustawień.',
 'Miejsce 1: kierowca','Miejsce 2: pasażer z przodu / strzelec','Miejsce 3: tył lewy / lewy pasażer / miotacz ognia','Miejsce 4: tył prawy / prawy pasażer','Miejsce 5: strzelec karabinu M-102'],
'ru':[
 'Версия','Обычная','Улучшенная','Источник назначений','Блокировать клавиши статистики',
 'Обычная сохраняет штатные группы мест. Улучшенная позволяет переходить между группами в одиночной и сетевой игре. Настройки применяются после завершения текущей смены места.',
 'INI и меню хранят назначения независимо. В меню клавиши изначально не назначены: настройте их на вкладке MODS. Переключение источника не перезаписывает назначения.',
 'Блокирует F2–F5 для монитора производительности. Клавиши смены мест работают. По умолчанию выключено.',
 'Активен INI. Для этих назначений выберите ModBindingsMenu в «Источник назначений».',
 'Место 1: водитель','Место 2: передний пассажир / стрелок','Место 3: сзади слева / левый пассажир / огнемёт','Место 4: сзади справа / правый пассажир','Место 5: пулемётчик M-102'],
}
def lua(v):
    if isinstance(v,str):return json.dumps(v,ensure_ascii=False)
    return '{'+','.join('['+lua(k)+']='+lua(x) for k,x in v.items())+'}'
def generate():
    entries={}
    for language,values in rows.items():
        assert len(values)==len(keys)
        strings={k:v for k,v in zip(keys,values)if k not in ['block_perf','perf_description']}
        assert len(strings['hint']+' | '+strings['seat1'])<=127,(language,'hint')
        for k,v in strings.items():assert len(v)<=(400 if k.endswith('description') else 127 if k.startswith('seat') or k=='hint' else 64),(language,k)
        entries[language]={'mod':'vehicle_specified_seat_switch','language':language,'strings':strings}
    data={'en':entries.pop('en'),'bundled':entries}
    (R/'src/menu_locales.lua').write_text('-- Authored translations; generated by make_locales.py.\nreturn '+lua(data)+'\n',encoding='utf-8')
    print('13 language tables validated')
if __name__=='__main__':generate()
