class redturtlechefcookie extends chefcookie {
    showSettings() {
        this.logTracking('settings_open');
        let el = document.querySelector('.chefcookie__settings-container');
        el.classList.add('chefcookie__settings-container--visible');
        el.style.minHeight = el.scrollHeight + 'px';
        setTimeout(() => {
            if (el.classList.contains('chefcookie__settings-container--visible')) {
                el.style.height = 'auto';
            }
        }, this.animationSpeed);
        this.fixMaxHeight();
    }
    acceptAllScripts() {
        let providers = [];
        this.config.settings.forEach(settings__value => {
            if (settings__value.scripts !== undefined) {
                Object.entries(settings__value.scripts).forEach(([scripts__key, scripts__value]) => {
                    this.accept(scripts__key, false);
                });
            }
        });
    }
    switchSettingsLabelsOpen() {
        document.querySelector('.chefcookie__button--accept').style.display = 'block';
        document.querySelector('.chefcookie__button--settings').style.display = 'none';
    }
    buildDom() {
        document.body.insertAdjacentHTML(
            'afterbegin',
            `
            <div id="cc-banner" class="chefcookie chefcookie--${this.config.style.layout} chefcookie--columns-${
                'columns' in this.config.style ? this.config.style.columns : 'auto'
            }${
                'scripts_selection' in this.config && this.config.scripts_selection !== false
                    ? ` chefcookie--has-scripts`
                    : ``
            } chefcookie--hidden">
                <div class="chefcookie__inner">
                    <div class="chefcookie__box">

                        <a data-cc-destroy href="#" class="close"></a>

                        <div class="chefcookie__message">${this.translate(this.config.message)}</div>
                        <div class="chefcookie__settings-container">
                            <ul class="chefcookie__groups chefcookie__groups--count-${this.config.settings.length}">
                                ${this.config.settings
                                    .map(
                                        (group, i) => `
                                    <li class="chefcookie__group${
                                        group.cannot_be_modified ? ` chefcookie__group--disabled` : ``
                                    }">
                                        <label class="chefcookie__group-label" for="chefcookie_group_${i}">
                                            <input${
                                                group.cannot_be_modified ? ` disabled="disabled"` : ``
                                            } class="chefcookie__group-checkbox" data-status="${this.isCheckboxActiveForGroup(
                                            i
                                        )}" id="chefcookie_group_${i}" type="checkbox" name="chefcookie_group[]" value="${i}"${
                                            this.isCheckboxActiveForGroup(i) === 2 ? ` checked="checked"` : ``
                                        } />
                                            <span class="chefcookie__group-title">${this.translate(group.title)}</span>
                                            <span class="chefcookie__group-checkbox-icon"></span>
                                            ${
                                                'description' in group && group.description != ''
                                                    ? `
                                            <span class="chefcookie__group-description">${this.translate(
                                                group.description
                                            )}</span>
                                            `
                                                    : ``
                                            }
                                            ${
                                                'scripts_selection' in this.config &&
                                                this.config.scripts_selection === 'collapse' &&
                                                'scripts' in group &&
                                                Object.keys(group.scripts).length > 0 &&
                                                Object.keys(group.scripts)[0].indexOf('dummy_') === -1
                                                    ? `
                                                        <a href="#" class="chefcookie__group-collapse">${
                                                            this.getLabel('group_open') != ''
                                                                ? this.getLabel('group_open')
                                                                : this.getLabel('settings_open')
                                                        }</a>
                                                    `
                                                    : ``
                                            }
                                        </label>
                                        ${
                                            'scripts_selection' in this.config &&
                                            this.config.scripts_selection !== false &&
                                            'scripts' in group &&
                                            Object.keys(group.scripts).length > 0 &&
                                            Object.keys(group.scripts)[0].indexOf('dummy_') === -1
                                                ? `
                                                <ul class="chefcookie__scripts chefcookie__scripts--count-${
                                                    Object.keys(group.scripts).length
                                                }${
                                                      this.config.scripts_selection !== 'collapse'
                                                          ? ` chefcookie__scripts--visible`
                                                          : ``
                                                  }">
                                                    ${Object.keys(group.scripts)
                                                        .map(
                                                            j => `
                                                        <li class="chefcookie__script${
                                                            group.cannot_be_modified
                                                                ? ` chefcookie__script--disabled`
                                                                : ``
                                                        }">
                                                            <label class="chefcookie__script-label" for="chefcookie_script_${i}_${j}">
                                                                <input${
                                                                    group.cannot_be_modified
                                                                        ? ` disabled="disabled"`
                                                                        : ``
                                                                } class="chefcookie__script-checkbox" id="chefcookie_script_${i}_${j}" type="checkbox" name="chefcookie_script[]" value="${i}|${j}"${
                                                                this.isCheckboxActiveForProvider(i, j)
                                                                    ? ` checked="checked"`
                                                                    : ``
                                                            } />
                                                                <span class="chefcookie__script-title">${
                                                                    typeof group.scripts[j] === 'object' &&
                                                                    group.scripts[j] !== null &&
                                                                    'title' in group.scripts[j] &&
                                                                    group.scripts[j].title != ''
                                                                        ? this.translate(group.scripts[j].title)
                                                                        : j
                                                                }</span>
                                                                <span class="chefcookie__script-checkbox-icon"></span>
                                                            </label>
                                                            ${
                                                                typeof group.scripts[j] === 'object' &&
                                                                group.scripts[j] !== null &&
                                                                'description' in group.scripts[j] &&
                                                                group.scripts[j].description != ''
                                                                    ? '<div class="chefcookie__script-description">' +
                                                                      '<a href="#" class="chefcookie__script-description-collapse">' +
                                                                      this.getLabel('details_open') +
                                                                      '</a>' +
                                                                      '<div class="chefcookie__script-description-content">' +
                                                                      this.translate(group.scripts[j].description) +
                                                                      '</div>' +
                                                                      '</div>'
                                                                    : ''
                                                            }
                                                        </li>
                                                    `
                                                        )
                                                        .join('')}
                                                </ul>
                                            `
                                                : ``
                                        }
                                    </li>
                                `
                                    )
                                    .join('')}
                            </ul>
                        </div>
                        <div class="chefcookie__buttons chefcookie__buttons--count-${
                            'show_decline_button' in this.config && this.config.show_decline_button === true ? '3' : '2'
                        }">
                            <a href="#chefcookie__decline" class="chefcookie__button chefcookie__button--decline">${this.getLabel(
                                'decline'
                            )}</a>
                        </div>
                    </div>
                </div>
            </div>
        `
        );
    }
}
